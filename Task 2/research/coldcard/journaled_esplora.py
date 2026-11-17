"""Journaled two-provider transport for fresh, fingerprint-pinned scopes.

Caller holds global and historical locks for the ENTIRE unit, validates its
published lease before passing lease_check, and durably backs up the journal.
The module has no retry, fallback or feature-promotion side effects.
"""
from datetime import datetime,timezone
import asyncio
import io
import gzip
import hashlib
import json
import time
import urllib.error
import urllib.request
from dual_api_frontier import PROVIDERS
from independent_mempool_pilot import require
from build_source_registry import json_bytes
from source_cohort import atomic_write
from prepare_frontier_checkpoint import write,sha

class TotalTimeoutOpener:
    """Same inherited proxy and verified TLS; aiohttp bounds the complete GET."""
    def open(self,url,timeout):
        async def request():
            import aiohttp
            bound=aiohttp.ClientTimeout(total=timeout,connect=timeout,sock_read=timeout)
            async with aiohttp.ClientSession(trust_env=True)as session:
                async with session.get(url,timeout=bound,allow_redirects=False)as response:
                    if response.status!=200:
                        raise urllib.error.HTTPError(url,response.status,response.reason,response.headers,None)
                    value=await response.read()
            result=io.BytesIO(value);result.status=200;return result
        return asyncio.run(request())

class JournaledEsplora:
    def __init__(self,provider,work,source_id,maximum,lease_check,opener=None,clock=time.monotonic,sleep=time.sleep):
        require(provider in PROVIDERS,'Unapproved provider')
        self.provider,self.work,self.sid,self.maximum=provider,work,source_id,maximum
        self.lease_check=lease_check;self.opener=opener or TotalTimeoutOpener()
        self.clock,self.sleep=clock,sleep;self.last=None;self.count=0;self.stopped=False
    def get(self,key,endpoint):
        require(not self.stopped,'Unit stopped; fresh scope required')
        require(endpoint.startswith('/')and'://'not in endpoint,'Invalid endpoint')
        require(key and all(c.isalnum()or c=='_'for c in key),'Invalid journal key')
        folder=self.work/'requests'/self.sid;folder.mkdir(parents=True,exist_ok=True)
        marker=folder/(key+'.json');body=folder/(key+'.json.gz')
        require(not marker.exists()and not body.exists(),'Consumed request cannot repeat')
        require(self.count<self.maximum,'Request budget exceeded')
        self.lease_check()
        while self.last is not None and self.clock()-self.last<5.25:
            self.sleep(5.25-(self.clock()-self.last))
        self.lease_check()
        meta=dict(source_id=self.sid,key=key,provider=self.provider,
            endpoint_sha256=hashlib.sha256(endpoint.encode()).hexdigest(),
            started_at=datetime.now(timezone.utc).isoformat())
        write(marker,meta);self.count+=1
        try:
            self.last=self.clock();meta.update(dispatch_at=datetime.now(timezone.utc).isoformat(),
                dispatch_monotonic=self.last,enforced_minimum_seconds=5.25)
            write(marker,meta)
            with self.opener.open(self.provider+endpoint,timeout=45)as response:
                require(response.status==200,'Unexpected HTTP status')
                value=json.loads(response.read())
            atomic_write(body,gzip.compress(json_bytes(value),mtime=0))
            meta.update(http_status=200,sha256=sha(body),provider_outcome='success');return value
        except BaseException as error:
            self.stopped=True;meta['error_type']=type(error).__name__;meta['provider_outcome']='unknown'
            if isinstance(error,urllib.error.HTTPError):
                meta['http_status']=error.code;meta['provider_outcome']='http_error'
                if error.headers and error.headers.get('Retry-After'):meta['retry_after']=error.headers['Retry-After']
            raise
        finally:
            meta['finished_at']=datetime.now(timezone.utc).isoformat();write(marker,meta)
