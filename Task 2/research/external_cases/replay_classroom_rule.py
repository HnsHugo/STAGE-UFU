"""Replay the saved classroom tree's class decisions on the central block cache.

This compares transaction alerts aggregated by recipient with collection counts.
No tree is fitted; unknown transactions and recipients remain unlabeled.
"""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re
from statistics import median
from rank_block_recipients import (coinbase, digest, load_protocol, rank_interval,
                                   validate_block)


def saved_rule(tree_text):
    pattern=(r'\|--- fee_sat <= ([0-9.]+)\n'
             r'\|   \|--- output_std_sat <= ([0-9.]+)\n\|   \|   \|--- class: 0\n'
             r'\|   \|--- output_std_sat >  \2\n\|   \|   \|--- class: 0\n'
             r'\|--- fee_sat >  \1\n\|   \|--- class: 1\n')
    match=re.fullmatch(pattern,tree_text)
    if not match:
        raise ValueError('Saved tree is not the supported equivalent fee rule')
    return float(match[1])


def classify_fee(fee, threshold):
    if type(fee) is not int or fee<0:
        raise ValueError('Fee must be nonnegative integer satoshis')
    return int(fee>threshold)


def run(protocol_path, summary_path, cache, course):
    protocol=load_protocol(protocol_path);summary=json.loads(summary_path.read_text())
    if summary['protocol_sha256']!=digest(protocol_path.read_bytes()):
        raise ValueError('Protocol checksum mismatch')
    tree_raw=(course/'tree.txt').read_bytes();threshold=saved_rule(tree_raw.decode())
    cohort_raw=(course/'cohort.csv').read_bytes()
    cohort=list(csv.DictReader(cohort_raw.decode().splitlines()))
    if len(cohort)!=200 or len({r['txid'] for r in cohort})!=200:
        raise ValueError('Unexpected classroom cohort')
    old_report=json.loads((course/'report.json').read_text())
    confusion=Counter()
    for row in cohort:
        predicted=classify_fee(int(row['fee_sat']),threshold)
        if row['split']=='test':
            confusion[(int(row['pays_course_address']=='True'),predicted)]+=1
    observed=dict(true_negative=confusion[(0,0)],false_positive=confusion[(0,1)],
                  false_negative=confusion[(1,0)],true_positive=confusion[(1,1)])
    if observed!={k:old_report['held_out_sample_proxy_metrics'][k] for k in observed}:
        raise ValueError('Saved classroom test confusion matrix does not reproduce')
    cohort_map={r['txid']:r['split'] for r in cohort}
    pinned={b['height']:b for b in summary['blocks']}
    groups={};seen=set()
    refs={r['address']:'reference_'+str(i+1) for i,r in enumerate(protocol['references'])}
    for entry in protocol['blocks']:
        raw=(cache/(str(entry['height'])+'.json')).read_bytes()
        if digest(raw)!=pinned[entry['height']]['raw_json_sha256']:
            raise ValueError('Raw-block checksum mismatch')
        block=json.loads(raw);validate_block(block,entry)
        group=groups.setdefault(entry['case_group'],dict(rows={},tx_count=0,alerts=0,
            cohort_overlap=Counter(),fees={},reference_observations={}))
        for tx in block['tx']:
            if tx['hash'] in seen:raise ValueError('Duplicate transaction across blocks')
            seen.add(tx['hash'])
            if coinbase(tx):continue
            fee=tx['fee'];flag=classify_fee(fee,threshold)
            previous=[i.get('prev_out') or {} for i in tx['inputs']]
            if any(type(i.get('value')) is not int for i in previous):
                raise ValueError('Missing input value for fee reconciliation')
            if sum(i['value'] for i in previous)-sum(o['value'] for o in tx['out'])!=fee:
                raise ValueError('Provider fee differs from input/output reconciliation')
            group['tx_count']+=1;group['alerts']+=flag
            split=cohort_map.get(tx['hash'])
            if split:group['cohort_overlap'][split]+=1
            recipients={o['addr'] for o in tx['out'] if o.get('addr') and o['value']>0}
            for address in recipients:
                row=group['rows'].setdefault(address,dict(flagged_receipt_transactions=0))
                row['flagged_receipt_transactions']+=flag
                if address in refs:
                    group['fees'].setdefault(address,[]).append(fee)
                    counts=group['reference_observations'].setdefault(address,Counter())
                    counts['receipts']+=1;counts['flagged']+=flag
                    if not split:counts['receipts_outside_cohort']+=1;counts['flagged_outside_cohort']+=flag
    output=[]
    for name,g in sorted(groups.items()):
        central=next(r for r in summary['pooled_results'] if r['case_group']==name)
        if len(g['rows'])!=central['recipient_count']:raise ValueError('Candidate population mismatch')
        comparisons=[]
        for ref in protocol['references']:
            if ref['case_group']!=name:continue
            address=ref['address'];fees=g['fees'].get(address,[])
            original=next(t for b in central['baselines'] if b['feature']=='single_output_external_funding_transaction_count'
                          for t in b['targets'] if t['reference_id']==refs[address])
            comparisons.append(dict(reference_id=refs[address],receipt_coverage=dict(g['reference_observations'].get(address,{})),
                fee_sat=dict(min=min(fees),median=median(fees),max=max(fees)) if fees else None,
                frozen_classroom_rank=rank_interval(g['rows'],address,'flagged_receipt_transactions'),
                fixed_collection_rank=original))
        output.append(dict(case_group=name,non_coinbase_transactions=g['tx_count'],transaction_alerts=g['alerts'],
             transaction_alert_fraction=g['alerts']/g['tx_count'],recipient_count=len(g['rows']),
             recipients_with_any_alert=sum(r['flagged_receipt_transactions']>0 for r in g['rows'].values()),
             classroom_cohort_transaction_overlap=dict(g['cohort_overlap']),references=comparisons))
    return dict(method='Exact class-decision equivalent of the saved tree, aggregated by distinct (TXID, recipient)',
        fee_threshold_sat=threshold,strict_greater_than=True,classroom_test_confusion_reproduced=observed,
        hashes=dict(protocol=digest(protocol_path.read_bytes()),central_summary=digest(summary_path.read_bytes()),
                    tree=digest(tree_raw),cohort=digest(cohort_raw),report=digest((course/'report.json').read_bytes())),
        groups=output,limits=['No fitting or threshold selection; tree class decisions only, not leaf probabilities',
        'Classroom labels mean payments to one address versus unattributed comparison rows',
        'Address alert counts are not hardware or theft labels; other outputs of flagged transactions remain unknown',
        'Coldcard is the training incident even after removing individual cohort transactions',
        'CryptoBilis has already informed other research; this is not an untouched prospective holdout',
        'Reference coverage and candidate ranks do not establish precision, F1 or calibrated probabilities',
        'Integer input/output/provider reconciliation is not cryptographic transaction verification'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('protocol','summary','cache','course','output'):p.add_argument(name,type=Path)
    a=p.parse_args();result=run(a.protocol,a.summary,a.cache,a.course)
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
