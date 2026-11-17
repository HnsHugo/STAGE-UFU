"""Provider-neutral frontier reconciliation; network/saving drivers remain explicit.

Never derive a pagination cursor from a TXID-sorted union. A switch replays a
complete-block overlap, using the selected provider's own sequence. Overlap
traffic is required evidence, not new transaction coverage.
"""
from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
import fcntl
from pathlib import Path
from independent_mempool_bridge import choose_bridge, merge_transaction
from independent_mempool_pilot import core, require, status_check

PROVIDERS=('https://mempool.space/api','https://blockstream.info/api')


def eligible_providers(gates, now=None):
    now=now or datetime.now(timezone.utc)
    result=[]
    for provider in PROVIDERS:
        gate=gates.get(provider,{})
        due=gate.get('next_network_attempt_not_before')
        if gate.get('status') in ('access_denied','disabled') or gate.get('last_http_status')==403:
            continue
        if due and now<datetime.fromisoformat(due):continue
        result.append(provider)
    return result


@contextmanager
def exclusive_run(lock_paths):
    """OS-owned lock lifetime, never cleared by deleting a lock or trusting ps."""
    with ExitStack()as stack:
        for name in sorted({str(Path(p).resolve())for p in lock_paths}):
            p=Path(name);p.parent.mkdir(parents=True,exist_ok=True)
            f=stack.enter_context(p.open('a+'))
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield


def collect_switch(record, anchor, saved_transactions, provider, get, checkpoint, max_pages=50):
    """Collect either direction; callers provide guarded journaled GET + durable save.

    `get(key, endpoint)` must record an intent before dispatch and save/hash the
    body before returning. `checkpoint(snapshot)` must atomically preserve each
    accepted page before the next GET. A failed page never moves the cursor.
    This returns evidence only: no complete feature row before an independent
    audit, reference/funding closure and durable private save.
    """
    require(provider in PROVIDERS,'Unapproved provider')
    require(0<max_pages<=50,'Invalid page bound')
    require(bool(saved_transactions),'Empty saved frontier')
    existing={}
    for tx in saved_transactions:
        require(tx['txid'] not in existing,'Duplicate saved TXID')
        existing[tx['txid']]=tx
    # A mixed union is not assumed to retain acquisition order. At the last
    # fully saved height any transaction in that block is a safe rewind point:
    # only overlap in that block may repeat, and the full partial block follows.
    ordered=sorted(existing.values(),key=lambda t:(-t['status']['block_height'],t['txid']))
    bridge,boundary=choose_bridge(record,anchor,ordered)
    status_check(record,get('reference_before','/tx/'+record['payment_txid']+'/status'))
    require(core(get('bridge','/tx/'+bridge['txid']))==core(bridge),'Bridge transaction differs')
    cursor=bridge['txid'];height=bridge['status']['block_height']
    seen={cursor};new=overlap=0;exhausted=False
    for index in range(max_pages):
        page=get(f'page_{index:04d}','/address/'+record['address']+'/txs/chain/'+cursor)
        require(isinstance(page,list)and len(page)<=25,'Invalid native page')
        # Validate a whole page before accepting it or advancing its cursor.
        candidate=dict(existing);candidate_seen=set(seen);next_height=height
        added=duplicates=0
        for tx in page:
            require(tx['status'].get('confirmed')is True and tx['status'].get('block_hash')and
                    tx['status']['block_height']<=next_height,'Invalid native block order')
            next_height=tx['status']['block_height']
            if merge_transaction(record,tx,candidate,candidate_seen,boundary):added+=1
            else:duplicates+=1
        next_cursor=page[-1]['txid']if page else cursor
        snapshot=dict(provider=provider,actual_native_cursor=next_cursor,partial_boundary_height=boundary,
            transactions=list(candidate.values()),native_pages=index+1,new_transactions=new+added,
            verified_overlap=overlap+duplicates,pagination_exhausted=not page,
            status='unfinished_evidence_not_promoted')
        checkpoint(snapshot)
        existing,seen,height,cursor=candidate,candidate_seen,next_height,next_cursor
        new+=added;overlap+=duplicates
        if not page:exhausted=True;break
    status_check(record,get('reference_after','/tx/'+record['payment_txid']+'/status'))
    return dict(snapshot,reference_after_verified=True,requires_independent_audit=True,
                requires_funding_closure=exhausted,features=None)
