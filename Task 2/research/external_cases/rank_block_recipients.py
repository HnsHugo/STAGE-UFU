"""Central experiment: rank all recipients of complete incident blocks.

Ranking is label-blind. Known collectors enter only the evaluation step.
Unreferenced recipients are not certified negative examples.
"""
import argparse
from collections import defaultdict
import csv
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import urllib.request

FEATURES = ('receipt_transaction_count', 'single_output_external_funding_transaction_count', 'received_sat')
FIELDS = ('address', *FEATURES)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def coinbase(tx):
    inputs = tx['inputs']
    if len(inputs) != 1:
        return False
    previous = inputs[0].get('prev_out') or {}
    return previous.get('tx_index') == 0 and previous.get('n') == 4294967295


def validate_block(block, reference):
    for key in ('height', 'hash', 'time'):
        if block[key] != reference[key]:
            raise ValueError('Block anchor mismatch: '+key)
    if not block.get('main_chain') or block['n_tx'] != len(block['tx']):
        raise ValueError('Incomplete or non-main-chain provider block')
    ids = [t['hash'] for t in block['tx']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate transaction in block')
    for tx in block['tx']:
        if tx['vin_sz'] != len(tx['inputs']) or tx['vout_sz'] != len(tx['out']):
            raise ValueError('Truncated transaction inputs or outputs')
        if [o['n'] for o in tx['out']] != list(range(len(tx['out']))):
            raise ValueError('Missing or duplicate transaction output index')
    if not block['tx'] or [i for i,t in enumerate(block['tx']) if coinbase(t)] != [0]:
        raise ValueError('Exactly one first-position coinbase required')


def recipient_features(transactions):
    """One count per (TXID, recipient); amounts sum all matching outputs."""
    rows, seen = {}, set()
    for tx in transactions:
        if tx['hash'] in seen:
            raise ValueError('Duplicate transaction')
        seen.add(tx['hash'])
        if coinbase(tx):
            continue
        amounts = defaultdict(int)
        for output in tx['out']:
            value = output['value']
            if type(value) is not int or value < 0:
                raise ValueError('Nonnegative integer satoshis required')
            if output.get('addr') and value > 0:
                amounts[output['addr']] += value
        inputs = [i.get('prev_out') or {} for i in tx['inputs']]
        for address, amount in amounts.items():
            row = rows.setdefault(address, dict(address=address, **dict.fromkeys(FEATURES, 0)))
            row['receipt_transaction_count'] += 1
            row['received_sat'] += amount
            external_one_output = len(tx['out']) == 1 and inputs and all(
                i.get('addr') not in (None, address) for i in inputs)
            row['single_output_external_funding_transaction_count'] += int(bool(external_one_output))
    return rows


def add_rows(total, rows):
    for address, row in rows.items():
        dest = total.setdefault(address, dict(address=address, **dict.fromkeys(FEATURES, 0)))
        for name in FEATURES:
            dest[name] += row[name]


def rank_interval(rows, address, feature):
    if address not in rows:
        return dict(observed=False, score=None, rank_best=None, rank_worst=None)
    score = rows[address][feature]
    above = sum(row[feature] > score for row in rows.values())
    equal = sum(row[feature] == score for row in rows.values())
    return dict(observed=True, score=score, rank_best=above+1, rank_worst=above+equal)


def evaluate(rows, references):
    return dict(recipient_count=len(rows), baselines=[dict(feature=feature,
        targets=[dict(address=a, **rank_interval(rows,a,feature)) for a in references],
        top10=[dict(address=r['address'], score=r[feature]) for r in sorted(
            rows.values(), key=lambda r: (-r[feature],r['address']))[:10]]) for feature in FEATURES])


def score_summary(rows, references):
    """Anonymous cumulative counts at reference/top-10 score values."""
    features = []
    for feature in FEATURES:
        scores = [r[feature] for r in rows.values()]
        cuts = {rows[a][feature] for a in references if a in rows}
        cuts.update(sorted(scores,reverse=True)[:10])
        points = [dict(score=s,less_count=sum(v<s for v in scores),
                       equal_count=sum(v==s for v in scores),greater_count=sum(v>s for v in scores))
                  for s in sorted(cuts)]
        features.append(dict(feature=feature,points=points))
    return dict(recipient_count=len(rows),features=features)


def target_features_from_history(history, hashes):
    txs = []
    for tx in history['transactions']:
        if tx['status']['block_hash'] not in hashes:
            continue
        inputs = [dict(prev_out=dict(addr=(i.get('prevout') or {}).get('scriptpubkey_address')))
                  for i in tx['vin']]
        outputs = [dict(addr=o.get('scriptpubkey_address'),value=o['value']) for o in tx['vout']]
        txs.append(dict(hash=tx['txid'],inputs=inputs,out=outputs))
    return recipient_features(txs).get(history['address'])


def verify_history_receipts(block, history):
    """Compare exact positive receipt outpoints against the pinned second API."""
    address = history['address']
    expected = {(t['txid'],n):o['value'] for t in history['transactions']
                if t['status']['block_hash'] == block['hash']
                for n,o in enumerate(t['vout']) if o.get('scriptpubkey_address') == address and o['value']>0}
    actual = {(t['hash'],o['n']):o['value'] for t in block['tx']
              for o in t['out'] if o.get('addr') == address and o['value']>0}
    if actual != expected:
        raise ValueError('Receipt mismatch between block and pinned address history')
    return dict(address=address, receipt_outpoints=len(actual), received_sat=sum(actual.values()),
                agreement='Exact receipt TXID, output index and value; not cryptographic verification')


def collect(protocol, cache):
    cache.mkdir(parents=True, exist_ok=True)
    for entry in protocol['blocks']:
        path = cache/(str(entry['height'])+'.json')
        if path.exists():
            validate_block(json.loads(path.read_bytes()),entry)
            continue
        url = 'https://blockchain.info/rawblock/'+entry['hash']+'?format=json'
        with urllib.request.urlopen(url, timeout=40) as response:
            raw = response.read()
        validate_block(json.loads(raw),entry)
        with path.open('xb') as stream:
            stream.write(raw)
        print('Collected block',entry['height'],flush=True)


def load_protocol(path):
    """Resolve optional source references from an existing checksummed registry."""
    protocol=json.loads(path.read_text())
    registry=protocol.get('reference_registry')
    if registry:
        raw=(path.parent/registry['file']).read_bytes()
        if digest(raw)!=registry['sha256']:
            raise ValueError('Reference registry checksum mismatch')
        candidates=[r for r in json.loads(raw)['records'] if r['source_id']==registry['source_id']]
        for ref in protocol['references']:
            record=candidates[ref['source_reference_index']]
            if record['conservative_split_group']!=ref['case_group']:
                raise ValueError('Reference incident group mismatch')
            ref['address']=record['address']
            ref['history_file']=str(Path(registry['history_directory'])/(record['address']+'.json'))
    return protocol


def load_references(protocol, base):
    histories = {}
    for ref in protocol['references']:
        path = base/ref['history_file']
        raw = path.read_bytes()
        if digest(raw) != ref['history_sha256']:
            raise ValueError('Reference history checksum mismatch')
        history = json.loads(gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw)
        if history['address'] != ref['address']:
            raise ValueError('Reference address mismatch')
        histories[ref['address']] = history
    return histories


def analyze(protocol_path, cache, destination):
    protocol = load_protocol(protocol_path)
    if protocol['baselines'] != list(FEATURES):
        raise ValueError('Protocol baseline mismatch')
    if destination.exists():
        raise ValueError('New output directory required')
    histories = load_references(protocol, protocol_path.parent)
    references = defaultdict(list)
    for ref in protocol['references']:
        references[ref['case_group']].append(ref['address'])
    totals, metadata, prefixes, all_txids = {}, [], [], set()
    for entry in sorted(protocol['blocks'],key=lambda r:r['height']):
        raw = (cache/(str(entry['height'])+'.json')).read_bytes()
        block = json.loads(raw)
        validate_block(block,entry)
        ids = {t['hash'] for t in block['tx']}
        if ids & all_txids:
            raise ValueError('Transaction repeated across selected blocks')
        all_txids.update(ids)
        group = entry['case_group']
        rows = recipient_features(block['tx'])
        total = totals.setdefault(group,{})
        add_rows(total,rows)
        agreements = [verify_history_receipts(block,histories[a]) for a in references[group]]
        metadata.append(dict(**entry, raw_json_sha256=digest(raw), raw_bytes=len(raw),
                             provider_url='https://blockchain.info/rawblock/'+entry['hash']+'?format=json',
                             transaction_count=block['n_tx'], non_coinbase_transactions=block['n_tx']-1,
                             decoded_recipient_count=len(rows), receipt_agreement=agreements,
                             p2a_anchor_output_count=sum(o.get('script')=='51024e73'
                                                         for t in block['tx'] for o in t['out'])))
        prefixes.append(dict(case_group=group, through_height=entry['height'],
                             **evaluate(total,references[group])))
    destination.mkdir()
    cohorts, pooled, summaries = [], [], []
    for group, rows in sorted(totals.items()):
        text = io.StringIO(newline='')
        writer = csv.DictWriter(text,fieldnames=FIELDS,lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows[a] for a in sorted(rows))
        raw = gzip.compress(text.getvalue().encode(),mtime=0)
        filename = group+'_recipients.csv.gz'
        (destination/filename).write_bytes(raw)
        cohorts.append(dict(case_group=group,file=filename,sha256=digest(raw),bytes=len(raw),rows=len(rows)))
        pooled.append(dict(case_group=group,**evaluate(rows,references[group])))
        summaries.append(dict(case_group=group,**score_summary(rows,references[group])))
    summary_raw = (json.dumps(dict(scope='Anonymous cumulative score counts; no full address list',
                                   groups=summaries),indent=2)+'\n').encode()
    (destination/'score_summary.json').write_bytes(summary_raw)
    overlap = []
    groups = sorted(totals)
    for i,left in enumerate(groups):
        for right in groups[i+1:]:
            overlap.append(dict(case_a=left,case_b=right,
                                shared_recipient_addresses=len(set(totals[left]) & set(totals[right])),
                                shared_reference_addresses=len(set(references[left]) & set(references[right]))))
    coverage = []
    for feature in FEATURES:
        by_case = []
        for result in pooled:
            targets = next(b['targets'] for b in result['baselines'] if b['feature']==feature)
            by_case.append(dict(case_group=result['case_group'],reference_count=len(targets),
                guaranteed_top10=sum(t['observed'] and t['rank_worst']<=10 for t in targets),
                possible_top10=sum(t['observed'] and t['rank_best']<=10 for t in targets)))
        coverage.append(dict(feature=feature,by_case=by_case,
                             interpretation='Coverage of supplied references, not sensitivity or precision over all thefts'))
    report = dict(schema_version=1,protocol_sha256=digest(protocol_path.read_bytes()),
                  analyzed_at=datetime.now(timezone.utc).isoformat(),
                  scope='Retrospective retrieval baseline on complete selected blocks; not a hardware classifier',
                  blocks=metadata,transaction_count=len(all_txids),prefix_results=prefixes,
                  pooled_results=pooled,cohorts=cohorts,reference_coverage_at_10=coverage,
                  cohort_address_overlap=overlap,
                  score_summary=dict(file='score_summary.json',sha256=digest(summary_raw),bytes=len(summary_raw)),
                  publication='Full recipient CSVs remain local; anonymous score summaries support offline reference-rank reproduction',
                  limits=['Block selection uses known incident receipts; not a blockchain-wide blind search',
                          'Baseline choice was informed by earlier case descriptions; no untouched external test is claimed',
                          'Reference set is incomplete; other recipients are not certified negatives',
                          f'{len(pooled)} incident groups; collector addresses are not independent incident observations',
                          'Gross receipts include change and internal transfers; values are not stolen totals',
                          'Provider anchors/counts and receipt agreement are not cryptographic block-inclusion proof',
                          'No address-to-device ground truth, calibrated probability, precision or F1 is estimated',
                          'Prefix ranking uses only complete blocks through that height, never later spending'])
    (destination/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    # Publish aggregate reference ranks, never the unknown-recipient address list.
    public = copy.deepcopy(report)
    aliases = {r['address']:'reference_'+str(i+1) for i,r in enumerate(protocol['references'])}
    for window in public['pooled_results']+public['prefix_results']:
        for baseline in window['baselines']:
            baseline['top10_scores'] = [r['score'] for r in baseline.pop('top10')]
            for target in baseline['targets']:
                target['reference_id'] = aliases[target.pop('address')]
    for block in public['blocks']:
        for agreement in block['receipt_agreement']:
            agreement['reference_id'] = aliases[agreement.pop('address')]
    public['publication'] = 'Anonymous aggregate ranks; full detailed rankings and recipient CSVs remain local'
    (destination/'summary.json').write_text(json.dumps(public,indent=2)+'\n')
    return report


def reproduce(result_dir, protocol_path):
    report = json.loads((result_dir/'summary.json').read_text())
    protocol = load_protocol(protocol_path)
    if digest(protocol_path.read_bytes()) != report['protocol_sha256']:
        raise ValueError('Protocol checksum mismatch')
    raw = (result_dir/report['score_summary']['file']).read_bytes()
    if digest(raw) != report['score_summary']['sha256']:
        raise ValueError('Score-summary checksum mismatch')
    summaries = {g['case_group']:g for g in json.loads(raw)['groups']}
    histories = load_references(protocol,protocol_path.parent)
    aliases = {'reference_'+str(i+1):r['address'] for i,r in enumerate(protocol['references'])}
    for expected in report['pooled_results']:
        group = expected['case_group']; summary = summaries[group]
        population = summary['recipient_count']
        if population != expected['recipient_count']:
            raise ValueError('Population mismatch')
        hashes = {b['hash'] for b in protocol['blocks'] if b['case_group']==group}
        by_feature = {f['feature']:f['points'] for f in summary['features']}
        for baseline in expected['baselines']:
            feature = baseline['feature']; points = by_feature[feature]
            for point in points:
                counts = [point[k] for k in ('less_count','equal_count','greater_count')]
                if any(type(n) is not int or n<0 for n in counts) or sum(counts)!=population:
                    raise ValueError('Invalid cumulative population counts')
            for target in baseline['targets']:
                observed = target_features_from_history(histories[aliases[target['reference_id']]],hashes)
                if observed is None or observed[feature] != target['score']:
                    raise ValueError('Target score differs from independent pinned history')
                point = next(p for p in points if p['score']==observed[feature])
                if (point['greater_count']+1,point['greater_count']+point['equal_count']) != (
                        target['rank_best'],target['rank_worst']):
                    raise ValueError('Reference ranking reproduction failed')
    return dict(status='passed',cohorts=len(report['cohorts']),reference_rankings_reproduced=True,
                target_scores_recomputed_from_pinned_histories=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    p = sub.add_parser('collect');p.add_argument('protocol',type=Path);p.add_argument('cache',type=Path)
    p = sub.add_parser('analyze');p.add_argument('protocol',type=Path);p.add_argument('cache',type=Path);p.add_argument('output',type=Path)
    p = sub.add_parser('reproduce');p.add_argument('results',type=Path);p.add_argument('protocol',type=Path)
    args = parser.parse_args()
    if args.command=='collect':
        collect(json.loads(args.protocol.read_text()),args.cache)
    elif args.command=='analyze':
        result=analyze(args.protocol,args.cache,args.output)
        print(json.dumps({'transactions':result['transaction_count'],'cohorts':result['cohorts']}))
    else:
        print(json.dumps(reproduce(args.results,args.protocol)))


if __name__=='__main__':
    main()
