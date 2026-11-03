"""Guarded, bounded CryptoBilis acquisition on the original declared routes.

Every actual attempt has a consumed marker. No internal retry, TLS override,
redirect, alternate provider or automatic successor is implemented here.
"""
import argparse
import asyncio
from contextlib import ExitStack, contextmanager
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import fcntl
import gzip
import json
from pathlib import Path
from threading import Event
import time
import urllib.error
import urllib.request

import select_cryptobilis_sources as selection
from select_cryptobilis_sources import ready, ROOT
from source_cohort import atomic_write
from comparison_http import PersistentHTTP
from collect_comparison_coverage import Pages
import collect_reference_tail as tail
import collect_reference_tail_many as batches
from rank_block_recipients import validate_block

POLICY = ROOT/'coldcard/comparison_access_retries_20261030/retry_policy.json'


def now():
    return datetime.now(timezone.utc)


def network_gate(policy, owner=None, clock=None):
    clock = clock or now()
    lease = policy.get('collector_lease', {})
    if lease.get('state') == 'running' and datetime.fromisoformat(lease['expires_at']) > clock:
        ready.require(owner is not None and lease.get('owner') == owner, 'Unexpired collector lease: no HTTP')
    if policy.get('next_network_attempt_not_before'):
        ready.require(datetime.fromisoformat(policy['next_network_attempt_not_before']) <= clock,
                      'Network cooldown is not due: no HTTP')


def backoff(policy, refusals):
    denied = [m for m in refusals if m.get('http_status') == 429]
    if not denied:
        return {}
    delay = min(86400, max(7200, 2*policy.get('last_retry_delay_seconds', 0)))
    due = max(datetime.fromisoformat(m['finished_at']) for m in denied)+timedelta(seconds=delay)
    for marker in denied:
        value = marker.get('retry_after')
        if value:
            try:
                server = datetime.fromisoformat(marker['finished_at'])+timedelta(seconds=max(0,int(value)))
            except ValueError:
                server = parsedate_to_datetime(value)
                if server.tzinfo is None:
                    server = server.replace(tzinfo=timezone.utc)
            due = max(due, server)
    return dict(last_retry_delay_seconds=delay, next_network_attempt_not_before=due.isoformat(),
                last_rate_limit_at=max(m['finished_at'] for m in denied))


@contextmanager
def held_locks(protocol, work, prefix=False):
    """Also check historical local locks; none of their files are truncated."""
    workspace = Path(protocol['workspace_root'])
    global_lock = workspace/'source_provider_collector.lock'
    paths = {global_lock}
    paths.update(workspace.glob('STAGE-UFU*/Task 2/research/**/collector.lock'))
    if prefix:
        paths.discard(work/'collector.lock')  # validated batch runner owns this lock
    else:
        paths.add(work/'collector.lock')
    with ExitStack() as stack:
        for path in sorted(paths):
            path.parent.mkdir(parents=True,exist_ok=True)
            stream = stack.enter_context(path.open('a+'))
            fcntl.flock(stream, fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield


class GuardedHTTP(PersistentHTTP):
    """Same transport/TLS, checking stop after the global rate-limit wait."""
    def __init__(self, requests_per_second=1):
        super().__init__(requests_per_second)
        self.stop = Event()

    async def request(self, url, timeout):
        ready.require(url.startswith('https://blockstream.info/api/'), 'Unexpected history route')
        async with self.lock:
            delay=max(0,self.next_start-self.loop.time())
            if delay:
                await asyncio.sleep(delay)
            if self.stop.is_set():
                raise InterruptedError('Stopped before HTTP dispatch')
            self.next_start=self.loop.time()+self.interval
        bound=self.aiohttp.ClientTimeout(total=timeout,connect=timeout,sock_read=timeout)
        try:
            async with self.client.get(url,timeout=bound,allow_redirects=False) as response:
                if response.status != 200:
                    self.stop.set()
                    raise urllib.error.HTTPError(url,response.status,response.reason,response.headers,None)
                return json.loads(await response.read())
        except self.aiohttp.ClientHttpProxyError as error:
            self.stop.set()
            raise urllib.error.HTTPError(url,error.status,'Original proxy refused CONNECT',error.headers,None) from error
        except Exception:
            self.stop.set()
            raise


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None


def collect_block(ref, work):
    folder=work/'block_requests'; folder.mkdir(exist_ok=True)
    marker=folder/(str(ref['height'])+'.json')
    destination=work/'blocks'/(str(ref['height'])+'.json')
    if marker.exists():
        meta=ready.read(marker)
        ready.require(destination.exists() and ready.sha(destination.read_bytes()) == meta.get('sha256'),
                      'Consumed block request cannot be retried internally')
        validate_block(json.loads(destination.read_bytes()),ref)
        return meta
    ready.require(not destination.exists(),'Unmanifested block cache requires separate recovery')
    url='https://blockchain.info/rawblock/'+ref['hash']+'?format=json'
    meta=dict(key='block_'+str(ref['height']),started_at=now().isoformat(),
              provider='https://blockchain.info',endpoint_sha256=ready.hashed(url),height=ref['height'])
    with marker.open('xb') as stream:
        stream.write(ready.encoded(meta))
    try:
        with urllib.request.build_opener(NoRedirect()).open(url,timeout=15) as response:
            ready.require(response.status == 200,'Block request was not HTTP200')
            raw=response.read()
        validate_block(json.loads(raw),ref)
        atomic_write(destination,raw)
        meta.update(http_status=200,sha256=ready.sha(raw),bytes=len(raw),finished_at=now().isoformat())
    except Exception as error:
        meta.update(error_type=type(error).__name__,finished_at=now().isoformat(),reason=str(error))
        if isinstance(error,urllib.error.HTTPError):
            meta['http_status']=error.code
            if error.headers and error.headers.get('Retry-After'):
                meta['retry_after']=error.headers['Retry-After']
        raise
    finally:
        atomic_write(marker,ready.encoded(meta))
    return meta


def validate_inputs(protocol):
    for pin in protocol['inputs'].values():
        path=ROOT/pin['file']
        ready.require(ready.sha(path.read_bytes()) == pin['sha256'],'Pinned input changed: '+pin['file'])


def run(protocol_path, output, work):
    protocol=ready.read(protocol_path)
    validate_inputs(protocol)
    work.mkdir(parents=True,exist_ok=True)
    with held_locks(protocol,work,prefix=protocol['stage']=='prefix'):
        network_gate(ready.read(POLICY))
        atomic_write(work/'locks_ready',ready.encoded(dict(at=now().isoformat(),http_requests=0)))
        print('GLOBAL_AND_HISTORICAL_LOCKS_HELD_NO_HTTP',flush=True)
        deadline=time.monotonic()+300
        while not (work/'lease_published').exists():
            if time.monotonic() > deadline:
                raise RuntimeError('No verified published lease; no HTTP')
            time.sleep(.25)
        policy=ready.read(POLICY)
        network_gate(policy,protocol['pass_name'])
        lease=policy['collector_lease']
        ready.require(lease.get('state')=='running' and lease.get('owner')==protocol['pass_name']
                      and lease.get('protocol_sha256')==ready.sha(protocol_path.read_bytes()),'Published lease does not match pass')
        output.mkdir(parents=True,exist_ok=True)
        try:
            if protocol['stage']=='census':
                first=ready.read(work/'preflight.json')
                with GuardedHTTP(1) as http:
                    pages=Pages(work,http,http.stop)
                    counter=pages.get(first,'availability_counter','/address/'+first['address'])
                    ready.require(counter.get('address')==first['address'],'Counter source mismatch')
                print('NORMAL_COUNTER_HTTP_200',flush=True)
                (work/'blocks').mkdir(exist_ok=True)
                for ref in protocol['blocks']:
                    time.sleep(1)
                    meta=collect_block(ref,work)
                    print('ANCHORED_BLOCK_HTTP_200 '+str(meta['height']),flush=True)
            else:
                ready.require(len(protocol['source_ids'])<=100,'More than five batches requested')
                tail.PersistentHTTP=GuardedHTTP
                # Reuse the validated tail and per-batch verifier without modifying their files.
                batches.main(protocol_path,output,work)
        except Exception as error:
            atomic_write(output/'collection_stop.json',ready.encoded(dict(stopped_at=now().isoformat(),
                reason=type(error).__name__+': '+str(error),automatic_retry_performed=False,
                provider_or_route_changed=False)))
            print('STOPPED '+type(error).__name__,flush=True)
        finally:
            requests=[ready.read(f) for f in sorted((work/'requests').glob('*/*.json'))]
            requests += [ready.read(f) for f in sorted((work/'block_requests').glob('*.json'))]
            atomic_write(output/'network_manifest.json.gz',gzip.compress(ready.encoded(requests),mtime=0))
            atomic_write(output/'run_stop.json',ready.encoded(dict(stopped_at=now().isoformat(),
                no_internal_retry=True,provider_or_route_changed=False,
                requests_marked=len(requests),failed_requests=[r for r in requests if 'error_type' in r])))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('protocol',type=Path); p.add_argument('output',type=Path); p.add_argument('work',type=Path)
    a=p.parse_args();run(a.protocol.resolve(),a.output.resolve(),a.work.resolve())
