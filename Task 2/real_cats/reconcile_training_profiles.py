"""Probe extraction conventions using complete histories of training addresses only."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from train_source_categories import HASHES, DROP, prepare, split
sys.path.insert(0,str(Path(__file__).parent.parent/'theft_cases'))
from collect_binance_research_seed import helper


def probes(address, transactions):
    incoming=[];outgoing=[];fees=[];rec_days=set();pay_days=set();all_days=set();sent_counter=received_counter=0
    receipt_count=payment_count=0
    for tx in transactions:
        ins=[v['prevout']['value'] for v in tx['vin'] if (v.get('prevout') or {}).get('scriptpubkey_address')==address]
        outs=[v['value'] for v in tx['vout'] if v.get('scriptpubkey_address')==address]
        day=datetime.fromtimestamp(tx['status']['block_time'],timezone.utc).date().isoformat();all_days.add(day)
        if outs:
            incoming.extend(outs);receipt_count+=1;rec_days.add(day)
            # Coinbase has no previous output or sending counterparty.
            sent_counter+=sum(not v.get('is_coinbase',False) and (v.get('prevout') or {}).get('scriptpubkey_address')!=address for v in tx['vin'])
        if ins:
            outgoing.extend(ins);payment_count+=1;pay_days.add(day)
            fees.append(tx['fee']*len(ins)/len(tx['vin']))
            received_counter+=len(ins)*sum(v.get('scriptpubkey_address')!=address for v in tx['vout'])
    times=[t['status']['block_time'] for t in transactions]
    values=dict(balance=sum(incoming)-sum(outgoing),total_received_BTC=sum(incoming),total_sent_BTC=sum(outgoing),
                transaction_fee=sum(fees),transaction_fee_Variance=float(np.var(fees)) if fees else 0,
                transaction_number=len(transactions),payment_transactions=payment_count,receipt_transactions=receipt_count,
                lifetime=max(times)-min(times),total_output_slots=len(incoming),total_input_slots=len(outgoing),
                activity_w=len(rec_days),activity_d=len(pay_days),activity_time=len(all_days),
                max_sent_amount=max(outgoing) if outgoing else None,min_sent_amount=min(outgoing) if outgoing else None,
                max_received_amount=max(incoming) if incoming else None,min_received_amount=min(incoming) if incoming else None,
                received_Variance_BTC=float(np.var(incoming)) if incoming else 0,
                sent_Variance_BTC=float(np.var(outgoing)) if outgoing else 0,sent_counters=sent_counter,received_counters=received_counter)
    alternatives=dict(activity_w_receipt_days=len(rec_days),activity_d_spending_days=len(pay_days),
                      fee_whole_outgoing_sum=sum(t['fee'] for t in transactions if any((v.get('prevout') or {}).get('scriptpubkey_address')==address for v in t['vin'])),
                      fee_sample_variance=float(np.var(fees,ddof=1)) if len(fees)>1 else 0,
                      received_sample_variance=float(np.var(incoming,ddof=1)) if len(incoming)>1 else 0,
                      sent_sample_variance=float(np.var(outgoing,ddof=1)) if len(outgoing)>1 else 0)
    return values,alternatives


def run(source, histories, output):
    if output.exists():raise ValueError('Output must be new')
    for name, expected in HASHES.items():
        with (source/name).open('rb') as handle:
            if hashlib.file_digest(handle,'sha256').hexdigest()!=expected:raise ValueError('Source checksum mismatch')
    data=prepare(pd.read_csv(source/'BB.tsv',sep='\t'),pd.read_csv(source/'CB.tsv',sep='\t'))
    train,_,_=split(data);allowed=set(data.iloc[train].address);rows=[];skipped=[]
    for folder in histories:
        for path in sorted(folder.glob('*.json')):
            h=json.loads(path.read_text())
            if not isinstance(h,dict) or 'transactions' not in h:continue
            address=h['address']
            if address not in allowed:
                skipped.append(dict(address=address,reason='Not a training reference'));continue
            audit=helper().check_history(address,h['transactions'],h['before'],h['after'],h['audit']['pagination_exhausted'])
            if not audit['coverage_complete_by_provider_counters']:raise ValueError('Incomplete reference history')
            source_row=data[data.address==address].iloc[0]
            last_minute=datetime.strptime(str(source_row.last_time),'%Y/%m/%d %H:%M').replace(tzinfo=timezone.utc)
            cutoff=int(last_minute.timestamp())+60
            historical=[t for t in h['transactions'] if t['status']['block_time']<cutoff]
            values,alternatives=probes(address,historical);comparisons={}
            for key,value in values.items():
                expected=float(source_row[key]);match=pd.isna(expected) if value is None else bool(np.isclose(value,expected,rtol=5e-3,atol=1e-6))
                comparisons[key]=dict(expected=None if pd.isna(expected) else expected,extracted=value,match=match)
            rows.append(dict(address=address,split='train',source_label=source_row.label,history_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                             comparisons=comparisons,alternatives=alternatives,reference_cutoff_exclusive_utc=datetime.fromtimestamp(cutoff,timezone.utc).isoformat(),excluded_later_transactions=len(h['transactions'])-len(historical)))
    if len({r['address'] for r in rows})!=len(rows):raise ValueError('Duplicate references')
    report=dict(status='Convention probes; adapter not certified',source_sha256=HASHES,references=rows,skipped=skipped,
                tolerance='rtol 0.005, atol 0.000001 to accommodate rounded TSV values',
                per_feature_matches={c:dict(matches=sum(r['comparisons'][c]['match'] for r in rows),references=len(rows)) for c in rows[0]['comparisons']},
                rule='No validation or reserved-test profile used to tune extraction; no model predictions')
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['per_feature_matches'],indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('histories',type=Path,nargs='+')
    a=p.parse_args();run(a.source,a.histories,a.output)
