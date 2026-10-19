"""Extract historical address features without using post-cutoff transactions."""
import argparse
import hashlib
import json
import statistics
from datetime import datetime, timezone, timedelta
from pathlib import Path


def timestamp(value):
    parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('UTC offset required')
    return int(parsed.timestamp())


def features_asof(address, transactions, cutoff, days):
    start=cutoff-days*86400
    if days<=0:
        raise ValueError('Positive window required')
    seen=set();receipts=[];spends=[];rates=[];active=set();observed=[]
    balance=0
    for tx in transactions:
        if tx['txid'] in seen:
            raise ValueError('Duplicate transaction')
        seen.add(tx['txid'])
        if not tx['status']['confirmed']:
            raise ValueError('Confirmed history required')
        when=tx['status']['block_time']
        if when>=cutoff:
            continue
        received=sum(o['value'] for o in tx['vout'] if o.get('scriptpubkey_address')==address)
        spent=sum(i['prevout']['value'] for i in tx['vin'] if i.get('prevout') and i['prevout'].get('scriptpubkey_address')==address)
        balance+=received-spent
        if when<start:
            continue
        if not received and not spent:
            raise ValueError('Unrelated transaction')
        observed.append(tx['txid'])
        active.add(datetime.fromtimestamp(when,timezone.utc).date().isoformat())
        if received:receipts.append(received)
        if spent:
            spends.append(spent)
            vsize=(tx['weight']+3)//4
            rates.append(tx['fee']/vsize)
    return dict(window_days=days,transaction_count=len(observed),receiving_transaction_count=len(receipts),
                spending_transaction_count=len(spends),received_sat=sum(receipts),spent_input_sat=sum(spends),
                net_flow_sat=sum(receipts)-sum(spends),balance_before_cutoff_sat=balance,
                mean_receipt_sat=statistics.mean(receipts) if receipts else None,
                max_receipt_sat=max(receipts) if receipts else None,
                mean_spent_input_sat=statistics.mean(spends) if spends else None,
                active_utc_days=len(active),transactions_per_day=len(observed)/days,
                median_outgoing_transaction_fee_rate=statistics.median(rates) if rates else None)


def run(history,registry,cutoff_text,days,output):
    cutoff=timestamp(cutoff_text)
    manifest=json.loads((history/'manifest.json').read_text())
    records=json.loads(registry.read_text())['records']
    if manifest['status']!='complete':raise ValueError('Incomplete provider history')
    result=[]
    by_address={x['address']:x for x in manifest['results']}
    for record in records:
        address=record['address'];entry=by_address[address]
        raw=(history/entry['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('History checksum mismatch')
        observation=json.loads(raw)
        if observation['address']!=address:raise ValueError('Address mismatch')
        result.append(dict(address=address,case_group=record['case_group'],role=record['role'],
                           evidence_level=record['evidence_level'],source_url=record['source_url'],
                           source_published_on=record['source_published_on'],asof_exclusive_utc=cutoff_text,
                           features=features_asof(address,observation['transactions'],cutoff,days)))
    report=dict(scope='Retrospective address observations; sourced roles, not a trained classifier',
                cutoff_policy='Transactions with block_time < cutoff; timestamps are provider block-time observations',
                label_policy='Source role recorded separately; exact publication time unknown; no universal transaction theft labels',
                window_start_utc=datetime.fromtimestamp(cutoff-days*86400,timezone.utc).isoformat(),
                registry_sha256=hashlib.sha256(registry.read_bytes()).hexdigest(),
                history_manifest_sha256=hashlib.sha256((history/'manifest.json').read_bytes()).hexdigest(),
                rows=result)
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'addresses':len(result),'transactions_in_window':sum(r['features']['transaction_count'] for r in result)}))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('history',type=Path);p.add_argument('registry',type=Path)
    p.add_argument('cutoff');p.add_argument('output',type=Path)
    p.add_argument('--days',type=int,default=7)
    a=p.parse_args();run(a.history,a.registry,a.cutoff,a.days,a.output)
