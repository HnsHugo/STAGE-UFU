"""Collect the uniquely matched Binance research seed; attribution remains inferred."""
import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


def helper():
    path=Path(__file__).parent.parent/'coldcard/collect_theft_seeds.py'
    spec=importlib.util.spec_from_file_location('history_checks',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def resolve(transaction):
    matches=[(i,o) for i,o in enumerate(transaction['vout'])
             if o.get('scriptpubkey_address','').startswith('bc1q')
             and o.get('scriptpubkey_address','').endswith('v3wm') and o['value']==56799700000]
    if len(matches)!=1:raise ValueError('Research identifier/amount does not uniquely match an output')
    return matches[0]


def run(transaction_path,output):
    output.mkdir(parents=True,exist_ok=False)
    transaction=json.loads(transaction_path.read_text())
    index,out=resolve(transaction);address=out['scriptpubkey_address']
    h=helper();base='https://blockstream.info/api'
    before=h.get(f'{base}/address/{address}')
    rows=[];cursor='';exhausted=False
    for _ in range(100):
        page=h.get(f'{base}/address/{address}/txs/chain'+(f'/{cursor}' if cursor else ''))
        if not page:exhausted=True;break
        rows.extend(page);cursor=page[-1]['txid']
    after=h.get(f'{base}/address/{address}')
    audit=h.check_history(address,rows,before,after,exhausted)
    if transaction['txid'] not in {t['txid'] for t in rows}:raise ValueError('Source transaction missing from collected history')
    record=dict(address=address,case_group='binance_2019',role='research_attributed_attacker_recipient',
                evidence_level='research_attribution_resolved_by_unique_prefix_suffix_amount_match',
                source_url='https://yong-wang.org/publication/23-SMC-Intention-Discovery.pdf',
                source_section='Section VII.F, page 6; abbreviated bc1q***v3wm and 567.997 BTC',
                incident_source='https://www.binance.com/en/support/announcement/detail/360028031711',
                source_published_on=None,source_available_at=None,hardware_control='unknown',
                matched_transaction=transaction['txid'],matched_output_index=index,
                caveats=['Complete address resolved from on-chain output, not fully printed in the paper',
                         'Paper introduction says 2017 while case section specifies 7 May 2019',
                         'No verified ownership or independent incident-role corroboration',
                         'Other transaction outputs remain unresolved'])
    result=dict(address=address,record=record,provider=base,collected_at=datetime.now(timezone.utc).isoformat(),
                audit=audit,before=before,after=after,transactions=rows)
    raw=(json.dumps(result,indent=2)+'\n').encode();(output/'history.json').write_bytes(raw)
    (output/'evidence.json').write_text(json.dumps(dict(record=record,history_sha256=hashlib.sha256(raw).hexdigest(),
        transaction_sha256=hashlib.sha256(transaction_path.read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps({'address':address,'audit':audit}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('transaction',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();run(a.transaction,a.output)
