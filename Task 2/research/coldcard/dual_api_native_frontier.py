"""Resume a saved same-provider cursor; never rewind or request old pages."""
from independent_mempool_native import validate_page
from independent_mempool_pilot import require,status_check
from dual_api_frontier import PROVIDERS

def collect_native(record,anchor,saved_transactions,provider,get,checkpoint,max_pages=50,*,cursor):
    require(provider in PROVIDERS and 0<max_pages<=50,'Invalid native scope')
    values=list(saved_transactions);seen={record['payment_txid']};height=record['cutoff_height']
    ordered=sorted(values,key=lambda t:(-t['status']['block_height'],t['txid']))
    for offset in range(0,len(ordered),25):height=validate_page(record,ordered[offset:offset+25],seen,height)
    require(any(t['txid']==cursor and t['status']['block_height']==height for t in values),'Cursor not on saved native frontier')
    status_check(record,get('reference_before','/tx/'+record['payment_txid']+'/status'));count=0
    for index in range(max_pages):
        page=get(f'page_{index:04d}','/address/'+record['address']+'/txs/chain/'+cursor)
        next_seen=set(seen);next_height=validate_page(record,page,next_seen,height)
        candidate=values+page;next_cursor=page[-1]['txid']if page else cursor
        snapshot=dict(provider=provider,actual_native_cursor=next_cursor,transactions=candidate,native_pages=index+1,new_transactions=count+len(page),verified_overlap=0,pagination_exhausted=not page,status='unfinished_evidence_not_promoted')
        checkpoint(snapshot);values,seen,height,cursor=candidate,next_seen,next_height,next_cursor;count+=len(page)
        if not page:break
    status_check(record,get('reference_after','/tx/'+record['payment_txid']+'/status'))
    return dict(snapshot,reference_after_verified=True,requires_independent_audit=True,requires_funding_closure=not page,features=None)
