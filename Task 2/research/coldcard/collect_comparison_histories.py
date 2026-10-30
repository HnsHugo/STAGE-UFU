"""One-pass resumable histories for the frozen same-block comparison sample."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import gzip
import json
from pathlib import Path
import time
from threading import Event
import urllib.error

from build_source_registry import digest, json_bytes
import prepayment_pilot as fixed
import source_cohort as saved
import source_comparison_design as design


def now():
    return datetime.now(timezone.utc).isoformat()


def make_plan(design_path, selection_path, cache):
    selected=json.loads(selection_path.read_bytes())
    regenerated=design.select(design_path,cache)
    if any(regenerated[k]!=selected[k] for k in selected if k!='snapshots'):
        raise ValueError('Block contents do not reproduce the frozen selection')
    protocol,_,_,_=design.load_design(design_path)
    blocks=[json.loads((cache/(str(b['height'])+'.json')).read_bytes()) for b in protocol['blocks']]
    first,transactions,_=design.census(blocks,protocol['blocks'])
    by_hash={digest(a.encode()):r for a,r in first.items()}
    if len(by_hash)!=len(first):raise ValueError('Ambiguous source hash')
    records=[]
    for row in selected['rows']:
        raw=by_hash[row['address_sha256']]
        tx=transactions[raw['reference_txid']][1]
        inputs=[i['prev_out'] for i in tx['inputs'] if (i.get('prev_out') or {}).get('addr')==raw['address']]
        record=dict(pilot_id=row['source_id'],address=raw['address'],address_sha256=row['address_sha256'],
                    payment_txid=raw['reference_txid'],payment_txid_sha256=digest(raw['reference_txid'].encode()),
                    cutoff_height=raw['cutoff_height'],cutoff_block_hash=raw['cutoff_block_hash'],
                    registry_input_slots=len(inputs),reference_input_value_sat=sum(i['value'] for i in inputs))
        if any(record[k]!=row[k] for k in ('payment_txid_sha256','cutoff_height','cutoff_block_hash')):
            raise ValueError('Reference identity mismatch during plan reconstruction')
        records.append(record)
    public=[{k:v for k,v in r.items() if k not in ('address','payment_txid')} for r in records]
    return records,public


def load(protocol_path):
    protocol=json.loads(protocol_path.read_bytes());root=protocol_path.parent
    for name,pin in protocol['inputs'].items():
        if digest((root/pin['file']).read_bytes())!=pin['sha256']:
            raise ValueError('Pinned collection input changed: '+name)
    public=json.loads(gzip.decompress((root/protocol['public_plan_file']).read_bytes()))
    if digest(json_bytes(public))!=protocol['public_plan_sha256']:
        raise ValueError('Public plan fingerprint mismatch')
    selected=json.loads((root/protocol['inputs']['selection']['file']).read_bytes())['rows']
    if 'network_recovery' in protocol:
        recovery=protocol['network_recovery']
        latest=baseline_entries(protocol_path,protocol)
        expected=[r['source_id'] for r in selected if r['source_id'] not in latest
                  or latest[r['source_id']]['status']=='error']
        if expected!=recovery['source_ids']:
            raise ValueError('Recovery changed the fixed network-gap selection')
        selected=[r for r in selected if r['source_id'] in set(expected)]
        check=json.loads((root/protocol['inputs']['access_check']['file']).read_bytes())
        if (check.get('accessible') is not True or check.get('http_status')!=200
                or check.get('url')!='https://blockstream.info/api/blocks/tip/height'
                or check.get('route')!='original_default_network_route'):
            raise ValueError('Recovery requires a successful original-route access check')
    expected_count=protocol.get('expected_source_count',1000)
    if len(public)!=expected_count or len({r['pilot_id'] for r in public})!=expected_count:
        raise ValueError('Unexpected fixed collection sample size')
    if [r['pilot_id'] for r in public]!=[r['source_id'] for r in selected]:
        raise ValueError('Collection source order changed')
    for r,s in zip(public,selected):
        if (any(r[k]!=s[k] for k in ('address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash'))
                or s['known_coldcard_core_membership']!=0
                or s['compromise_label'] is not None or s['hardware_label'] is not None):
            raise ValueError('Collection source/label mismatch')
    if (protocol['provider']!='https://blockstream.info/api' or protocol['workers']!=2
            or protocol['max_pages_per_address']!=16 or protocol['timeout_seconds']!=15
            or protocol['default_batch_size']!=20 or protocol['attempts_per_source']!=1):
        raise ValueError('Frozen collection bounds changed')
    transport=protocol.get('http_transport',{})
    if transport.get('keepalive') and (transport.get('connections')!=2
            or not 0<transport.get('requests_per_second',0)<=3):
        raise ValueError('Persistent transport exceeded collection limits')
    return protocol,public


def previous_recovery(protocol_path,protocol):
    """A single cooldown continuation may pin the preserved stopped recovery."""
    prior=protocol.get('network_recovery',{}).get('prior_recovery')
    if prior is None:return None
    root=protocol_path.parent;inputs=protocol['inputs']
    previous_protocol=root/inputs[prior['protocol_input']]['file']
    previous_checkpoint=root/inputs[prior['checkpoint_input']]['file']
    old,public=load(previous_protocol)
    if ('network_recovery' not in old or old['network_recovery'].get('prior_recovery')
            or any(old['inputs'][k]!=inputs[k] for k in ('baseline_protocol','baseline_checkpoint','selection'))):
        raise ValueError('Continuation changed the original comparison lineage')
    state=json.loads(gzip.decompress(previous_checkpoint.read_bytes()))
    validate(state,previous_protocol,public)
    stop=json.loads((root/inputs[prior['stop_input']]['file']).read_bytes())
    errors=[e for e in state['entries'].values() if provider_denied(e)]
    if (not errors or any(e.get('http_status')!=429 for e in errors)
            or stop.get('http_statuses')!=[429]
            or stop.get('checkpoint_sha256')!=digest(previous_checkpoint.read_bytes())):
        raise ValueError('Cooldown continuation is restricted to saved HTTP 429 rate limits')
    last=max(datetime.fromisoformat(e['request_finished_at']) for e in errors)
    cooldown=protocol.get('rate_limit_recovery',{})
    earliest=datetime.fromisoformat(cooldown['not_before'])
    if ((earliest-last).total_seconds()<900 or
            not 0<protocol.get('http_transport',{}).get('requests_per_second',0)<=1):
        raise ValueError('Continuation requires fifteen-minute cooldown and at most one request/second')
    return previous_protocol,previous_checkpoint,old,state


def baseline_entries(protocol_path,protocol):
    root=protocol_path.parent
    initial=json.loads(gzip.decompress((root/protocol['inputs']['baseline_checkpoint']['file']).read_bytes()))
    latest=deepcopy(initial['entries']);prior=previous_recovery(protocol_path,protocol)
    if prior:
        for key,e in prior[3]['entries'].items():
            if key in latest and latest[key]['status']!='error':
                raise ValueError('A previous pass overwrote a complete/incomplete result')
            latest[key]=deepcopy(e)
    return latest


def check_cooldown(protocol):
    if 'rate_limit_recovery' in protocol:
        if datetime.now(timezone.utc)<datetime.fromisoformat(protocol['rate_limit_recovery']['not_before']):
            raise ValueError('Rate-limit cooldown has not elapsed; no request started')


def private_plan(protocol_path,work,cache):
    protocol,public=load(protocol_path)
    path=work/'plan.json'
    if path.exists():records=json.loads(path.read_bytes())
    else:
        if cache is None:raise ValueError('Reconstruction needs the four-block cache')
        root=protocol_path.parent
        records,regenerated=make_plan(root/protocol['inputs']['design']['file'],
                                     root/protocol['inputs']['selection']['file'],cache)
        if 'network_recovery' in protocol:
            allowed=set(protocol['network_recovery']['source_ids'])
            records=[r for r in records if r['pilot_id'] in allowed]
            regenerated=[r for r in regenerated if r['pilot_id'] in allowed]
        if regenerated!=public:raise ValueError('Reconstructed public plan changed')
        saved.atomic_write(path,json_bytes(records))
    if digest(json_bytes(records))!=protocol['private_plan_sha256']:
        raise ValueError('Private plan fingerprint mismatch')
    if [{k:v for k,v in r.items() if k not in ('address','payment_txid')} for r in records]!=public:
        raise ValueError('Private/public plan mismatch')
    for r in records:
        if digest(r['address'].encode())!=r['address_sha256'] or digest(r['payment_txid'].encode())!=r['payment_txid_sha256']:
            raise ValueError('Private identifier hash mismatch')
    return protocol,public,{r['pilot_id']:r for r in records}


def validate(state,protocol_path,public,work=None):
    saved.validate(state,protocol_path,public,work)
    expected={r['pilot_id']:r for r in public}
    assigned=[key for b in state['batches'] for key in b['source_ids']]
    if assigned!=[r['pilot_id'] for r in public][:len(assigned)]:
        raise ValueError('Collection changed fixed batch order')
    if not set(state['entries'])<=set(assigned):raise ValueError('Unassigned collection result')
    offset=0;order=[r['pilot_id'] for r in public]
    for batch in state['batches']:
        planned=batch.get('planned_source_ids',batch['source_ids'])
        if planned!=order[offset:offset+len(planned)] or batch['source_ids']!=planned[:len(batch['source_ids'])]:
            raise ValueError('Partial batch altered the original planned order')
        offset+=len(batch['source_ids'])
    for key,e in state['entries'].items():
        r=expected[key]
        if (e['known_coldcard_core_membership']!=0 or e['attempt_count']!=1
                or e['payment_txid_sha256']!=r['payment_txid_sha256']
                or e['cutoff_block_hash']!=r['cutoff_block_hash']):
            raise ValueError('Checkpoint target/reference/attempt changed')


def entry_base(record,marker):
    entry=saved.base_entry(record,'network')
    entry.update(known_coldcard_core_membership=0,payment_txid_sha256=record['payment_txid_sha256'],
                 cutoff_block_hash=record['cutoff_block_hash'],attempt_count=1,
                 request_started_at=marker['started_at'],request_finished_at=marker.get('finished_at'))
    return entry


def from_raw(record,raw,marker):
    history=json.loads(gzip.decompress(raw))
    entry=entry_base(record,marker)
    entry.update(raw_file=f"raw/{record['pilot_id']}.json.gz",raw_sha256=digest(raw),raw_bytes=len(raw))
    try:
        converted=saved.from_history(record,history,raw,'network')
        if converted['status']=='complete':
            tx=next(t for t in history['transactions'] if t['txid']==record['payment_txid'])
            inputs=[i for i in tx['vin'] if (i.get('prevout') or {}).get('scriptpubkey_address')==record['address']]
            if (len(inputs)!=record['registry_input_slots'] or
                    sum(i['prevout']['value'] for i in inputs)!=record['reference_input_value_sat']):
                raise ValueError('History reference source input count/value differs from block evidence')
        entry.update(converted)
        entry['collection_mode']=history.get('collection_mode','original_bounded_pagination')
    except Exception as error:
        entry.update(status='error',features=None,prefix=None,reason=type(error).__name__+': '+str(error),
                     error_type=type(error).__name__)
    return entry


def bounded_collect_one(record,protocol,get_json=None):
    """Skip provably insufficient pagination without changing completeness rules.

    Esplora /txs/chain pages contain at most 25 confirmed transactions. If the
    initial count exceeds 16*25, this bound cannot exhaust the history. Preserve
    both counter responses and an explicitly incomplete empty evidence list.
    """
    address=record['address'];base=protocol['provider']
    def get(endpoint):return (get_json or fixed.get_json)(base+endpoint,protocol['timeout_seconds'])
    before=get('/address/'+address)
    count=before['chain_stats']['tx_count']
    if type(count) is not int or count<0:raise ValueError('Invalid provider transaction counter')
    transactions=[];exhausted=False;cursor='';pages=0
    over_capacity=count>25*protocol['max_pages_per_address']
    if not over_capacity:
        for _ in range(protocol['max_pages_per_address']):
            page=get('/address/'+address+'/txs/chain'+('/'+cursor if cursor else ''))
            pages+=1
            if not page:exhausted=True;break
            if len(page)>25:raise ValueError('Provider exceeded documented pagination capacity')
            transactions.extend(page);cursor=page[-1]['txid']
    after=get('/address/'+address)
    if before.get('address')!=address or after.get('address')!=address:
        raise ValueError('Provider address mismatch')
    audit=fixed.check_history(address,transactions,before,after,exhausted)
    return dict(address=address,provider=base,before=before,after=after,audit=audit,
                transactions=transactions,collected_at=now(),pages_fetched=pages,
                collection_mode='counter_capacity_precheck' if over_capacity else 'bounded_pagination',
                page_capacity=25*protocol['max_pages_per_address'])


def fetch_one(record,protocol,work,get_json=None,stop=None):
    if stop is not None and stop.is_set():return None
    marker_path=work/'attempts'/f"{record['pilot_id']}.json"
    marker=dict(source_id=record['pilot_id'],started_at=now())
    marker_path.parent.mkdir(parents=True,exist_ok=True)
    # Persist before HTTP: interrupted attempts cannot be silently retried.
    with marker_path.open('xb') as stream:stream.write(json_bytes(marker))
    try:
        history=bounded_collect_one(record,protocol,get_json) if get_json else bounded_collect_one(record,protocol)
        raw=gzip.compress(json_bytes(history),mtime=0)
        path=work/'raw'/f"{record['pilot_id']}.json.gz"
        if path.exists():raise FileExistsError('Raw evidence already exists')
        saved.atomic_write(path,raw)
        marker.update(finished_at=now(),raw_sha256=digest(raw))
    except Exception as error:
        marker.update(finished_at=now(),error_type=type(error).__name__,reason=type(error).__name__+': '+str(error))
        if isinstance(error,urllib.error.HTTPError):
            marker['http_status']=error.code
            if error.headers and error.headers.get('Retry-After'):
                marker['retry_after']=str(error.headers['Retry-After'])[:256]
        if stop is not None and provider_denied(marker):stop.set()
    saved.atomic_write(marker_path,json_bytes(marker))
    return record['pilot_id']


def recover_entry(record,work):
    marker_path=work/'attempts'/f"{record['pilot_id']}.json"
    raw_path=work/'raw'/f"{record['pilot_id']}.json.gz"
    if not marker_path.exists():
        if raw_path.exists():raise ValueError('Raw history without an attempt marker')
        return None
    marker=json.loads(marker_path.read_bytes())
    if marker['source_id']!=record['pilot_id']:raise ValueError('Attempt marker source mismatch')
    if raw_path.exists():
        raw=raw_path.read_bytes()
        if marker.get('raw_sha256') and marker['raw_sha256']!=digest(raw):
            raise ValueError('Attempt/raw fingerprint mismatch')
        return from_raw(record,raw,marker)
    e=entry_base(record,marker)
    e.update(reason=marker.get('reason','InterruptedAttempt: no complete raw response saved; not retried'),
             error_type=marker.get('error_type','InterruptedAttempt'))
    if 'http_status' in marker:e['http_status']=marker['http_status']
    if 'retry_after' in marker:e['retry_after']=marker['retry_after']
    return e


def counts(state,public):
    entries=state['entries'];totals=Counter(e['status'] for e in entries.values())
    strata=[]
    for height in sorted({r['cutoff_height'] for r in public}):
        ids=[r['pilot_id'] for r in public if r['cutoff_height']==height]
        c=Counter(entries[k]['status'] for k in ids if k in entries)
        strata.append(dict(height=height,selected=len(ids),complete=c['complete'],incomplete=c['incomplete'],
                           errors=c['error'],pending=sum(k not in entries for k in ids)))
    return dict(selected_sources=len(public),attempted_sources=len(entries),complete_sources=totals['complete'],
                incomplete_sources=totals['incomplete'],error_sources=totals['error'],pending_sources=len(public)-len(entries),
                by_reference_block=strata,error_types=dict(sorted(Counter(e.get('error_type','unknown')
                    for e in entries.values() if e['status']=='error').items())),
                prior_transaction_observations=sum(e['features']['confirmed_tx_count'] for e in entries.values() if e['status']=='complete'),
                sources_with_prior_spending=sum(e['features']['spending_tx_count']>0 for e in entries.values() if e['status']=='complete'),
                feature_count=14,comparison_compromise_hardware_labels='unknown',training_performed=False)


def provider_denied(entry):
    if entry.get('http_status') in (403,429):return True
    # urllib reports a refused HTTPS CONNECT as URLError, not HTTPError.
    reason=entry.get('reason','')
    return entry.get('error_type')=='URLError' and any(
        f'Tunnel connection failed: {code}' in reason for code in (403,429))


def denied_batch(state,batch):
    return bool(batch['source_ids']) and any(provider_denied(state['entries'].get(key,{}))
                                            for key in batch['source_ids'])


def batch_bytes(state,batch):
    return gzip.compress(json_bytes(dict(batch=batch,entries={k:state['entries'][k] for k in batch['source_ids']})),mtime=0)


def save_batch(state,batch,output):
    path=output/f"batch_{batch['batch_id']:04d}.json.gz";raw=batch_bytes(state,batch)
    if path.exists():
        if path.read_bytes()!=raw:raise ValueError('Immutable batch export changed')
    else:saved.atomic_write(path,raw)
    return dict(file=path.name,sha256=digest(raw),source_count=len(batch['source_ids']))


def export_latest(protocol_path,state,public,output):
    validate(state,protocol_path,public)
    manifest=[save_batch(state,b,output) for b in state['batches'] if b['status']=='completed']
    rows=[]
    for r in public:
        e=state['entries'].get(r['pilot_id'])
        rows.append(dict(source_id=r['pilot_id'],address_sha256=r['address_sha256'],
            payment_txid_sha256=r['payment_txid_sha256'],cutoff_height=r['cutoff_height'],
            status=e['status'] if e else 'pending',features=e['features'] if e else None,
            known_coldcard_core_membership=0,compromise_label=None,hardware_label=None))
    for name,raw in {
        'checkpoint.json.gz':gzip.compress(json_bytes(state),mtime=0),
        'features.json.gz':gzip.compress(json_bytes(rows),mtime=0),
        'progress.json':json_bytes(counts(state,public)),
        'batches.json':json_bytes(dict(protocol_sha256=digest(protocol_path.read_bytes()),batches=manifest))}.items():
        saved.atomic_write(output/name,raw)


def verify(protocol_path,output,work=None):
    _,public=load(protocol_path)
    state=json.loads(gzip.decompress((output/'checkpoint.json.gz').read_bytes()))
    validate(state,protocol_path,public,work)
    manifest=json.loads((output/'batches.json').read_bytes())
    if manifest['protocol_sha256']!=digest(protocol_path.read_bytes()):raise ValueError('Batch protocol mismatch')
    if len(manifest['batches'])!=len(state['batches']) or any(b['status']!='completed' for b in state['batches']):
        raise ValueError('Final export contains an unfinished/unexported batch')
    merged={}
    for b,pin in zip(state['batches'],manifest['batches']):
        raw=(output/pin['file']).read_bytes()
        if digest(raw)!=pin['sha256'] or raw!=batch_bytes(state,b):raise ValueError('Batch evidence mismatch')
        part=json.loads(gzip.decompress(raw))['entries']
        if set(merged)&set(part):raise ValueError('Repeated source in batch deltas')
        merged.update(part)
    if merged!=state['entries']:raise ValueError('Batch/checkpoint evidence mismatch')
    rows=json.loads(gzip.decompress((output/'features.json.gz').read_bytes()))
    if len(rows)!=len(public) or len({r['source_id'] for r in rows})!=len(public):raise ValueError('Feature export coverage mismatch')
    for row,r in zip(rows,public):
        e=state['entries'].get(r['pilot_id'])
        expected=dict(source_id=r['pilot_id'],address_sha256=r['address_sha256'],payment_txid_sha256=r['payment_txid_sha256'],
                      cutoff_height=r['cutoff_height'],status=e['status'] if e else 'pending',features=e['features'] if e else None,
                      known_coldcard_core_membership=0,compromise_label=None,hardware_label=None)
        if row!=expected:raise ValueError('Feature export differs from normalized evidence')
    if (output/'progress.json').read_bytes()!=json_bytes(counts(state,public)):
        raise ValueError('Coverage summary mismatch')
    return counts(state,public)


def run_many(protocol_path,work,output,max_batches=50,cache=None,restore=None):
    if type(max_batches) is not int or max_batches<1:raise ValueError('Positive max_batches required')
    work.mkdir(parents=True,exist_ok=True);output.mkdir(parents=True,exist_ok=True)
    with (work/'collector.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        protocol,public,private=private_plan(protocol_path,work,cache)
        check_cooldown(protocol)
        if protocol.get('http_transport',{}).get('keepalive'):
            from comparison_http import PersistentHTTP
            with PersistentHTTP(protocol['http_transport']['requests_per_second']) as http:
                return run_locked(protocol_path,work,output,max_batches,restore,protocol,public,private,http.get_json)
        return run_locked(protocol_path,work,output,max_batches,restore,protocol,public,private)


def run_locked(protocol_path,work,output,max_batches,restore,protocol,public,private,get_json=None):
    state_path=work/'state.json'
    if state_path.exists():state=json.loads(state_path.read_bytes())
    elif restore is not None:state=json.loads(gzip.decompress(restore.read_bytes()))
    else:state=saved.empty_state(protocol_path,public)
    validate(state,protocol_path,public,work)
    # Repair a completed export before allowing any next-batch HTTP requests.
    completed=deepcopy(state)
    completed['batches']=[b for b in state['batches'] if b['status']=='completed']
    finished={key for b in completed['batches'] for key in b['source_ids']}
    completed['entries']={k:e for k,e in state['entries'].items() if k in finished}
    export_latest(protocol_path,completed,public,output);verify(protocol_path,output)
    started=time.monotonic();done=0
    while True:
        active=next((b for b in state['batches'] if b['status']=='running'),None)
        if active is None:
            if state['batches'] and denied_batch(state,state['batches'][-1]):
                print('Stopped: last batch was denied; no new requests on resume',flush=True);break
            if len(state['entries'])==len(public) or done>=max_batches:break
            ids=[r['pilot_id'] for r in public if r['pilot_id'] not in state['entries']][:protocol['default_batch_size']]
            active=dict(batch_id=len(state['batches'])+1,source_ids=ids,status='running',
                        collector_sha256=digest(Path(__file__).read_bytes()))
            state['batches'].append(active);saved.atomic_write(state_path,json_bytes(state))
        # Complete raw orphans; consume interrupted started attempts without HTTP retry.
        for key in active['source_ids']:
            if key not in state['entries']:
                recovered=recover_entry(private[key],work)
                if recovered is not None:
                    state['entries'][key]=recovered;saved.atomic_write(state_path,json_bytes(state))
        stop=Event()
        if any(provider_denied(state['entries'].get(key,{})) for key in active['source_ids']):stop.set()
        selected=[key for key in active['source_ids'] if key not in state['entries']]
        with ThreadPoolExecutor(max_workers=protocol['workers']) as pool:
            pending={pool.submit(fetch_one,private[key],protocol,work,get_json,stop):key for key in selected}
            for future in as_completed(pending):
                key=pending[future];future.result()
                entry=recover_entry(private[key],work)
                if entry is None:continue
                state['entries'][key]=entry
                saved.atomic_write(state_path,json_bytes(state))
                print(key+': '+entry['status'],flush=True)
        if stop.is_set():
            planned=list(active['source_ids'])
            attempted=[key for key in planned if key in state['entries']]
            if attempted!=planned[:len(attempted)] or not attempted:
                raise ValueError('Denied batch has a non-prefix attempt set')
            active.update(planned_source_ids=planned,source_ids=attempted,stopped_due_to_denial=True)
        active['status']='completed';validate(state,protocol_path,public,work)
        saved.atomic_write(state_path,json_bytes(state))
        export_latest(protocol_path,state,public,output)
        verify(protocol_path,output)
        done+=1
        print(json.dumps(dict(batch=active['batch_id'],elapsed_seconds=round(time.monotonic()-started,1),
                              coverage=counts(state,public))),flush=True)
        if denied_batch(state,active):
            print('Stopped: network access denied; unstarted sources remain pending',flush=True);break
    export_latest(protocol_path,state,public,output)
    return verify(protocol_path,output)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('run-many','verify'))
    parser.add_argument('protocol',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--work',type=Path);parser.add_argument('--cache',type=Path)
    parser.add_argument('--restore',type=Path);parser.add_argument('--max-batches',type=int,default=50)
    args=parser.parse_args()
    if args.command=='run-many':
        if args.work is None:parser.error('run-many requires --work')
        result=run_many(args.protocol,args.work,args.output,args.max_batches,args.cache,args.restore)
    else:result=verify(args.protocol,args.output,args.work)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
