"""Bounded historical collection and equal-maturity retrospective snapshots."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from collect_binance_research_seed import helper
from extract_asof_features import features_asof


def collect(record):
    h=helper();address=record['address'];base='https://blockstream.info/api'
    if not address.startswith('bc1'):h.validate_address(address)
    before=h.get(f'{base}/address/{address}')
    if before['address']!=address:raise ValueError('Provider address mismatch')
    transactions=[];cursor='';exhausted=False
    for _ in range(6):
        page=h.get(f'{base}/address/{address}/txs/chain'+(f'/{cursor}' if cursor else ''))
        if not page:exhausted=True;break
        transactions.extend(page);cursor=page[-1]['txid']
    after=h.get(f'{base}/address/{address}')
    audit=h.check_history(address,transactions,before,after,exhausted)
    snapshot=None
    if audit['coverage_complete_by_provider_counters'] and transactions:
        receipts=[t['status']['block_time'] for t in transactions if any(o.get('scriptpubkey_address')==address for o in t['vout'])]
        if receipts:
            cutoff=min(receipts)+86400
            snapshot=dict(asof_exclusive_utc=datetime.fromtimestamp(cutoff,timezone.utc).isoformat(),
                          features=features_asof(address,transactions,cutoff,7),
                          label_available_at=record['label_available_at'],training_label='pending_evidence_review')
    return dict(address=address,source_record=record,provider=base,collected_at=datetime.now(timezone.utc).isoformat(),
                before=before,after=after,audit=audit,transactions=transactions,snapshot=snapshot)


def run(selection,output):
    output.mkdir(parents=True,exist_ok=False)
    records=json.loads(selection.read_text())['records'];results=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(collect,r):r for r in records}
        for future in as_completed(futures):
            record=futures[future]
            try:
                data=future.result();raw=(json.dumps(data,indent=2)+'\n').encode()
                filename=record['address']+'.json';(output/filename).write_bytes(raw)
                result=dict(address=record['address'],file=filename,sha256=hashlib.sha256(raw).hexdigest(),audit=data['audit'],snapshot=data['snapshot'])
            except Exception as e:result=dict(address=record['address'],error=str(e))
            results.append(result)
            complete=len(results)==len(records) and all(x.get('audit',{}).get('coverage_complete_by_provider_counters') and x.get('snapshot') for x in results)
            report=dict(status='complete' if complete else 'incomplete',selection_sha256=hashlib.sha256(selection.read_bytes()).hexdigest(),
                        max_pages_per_address=6,workers=2,results=sorted(results,key=lambda r:r['address']))
            (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(result),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('selection',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();run(a.selection,a.output)
