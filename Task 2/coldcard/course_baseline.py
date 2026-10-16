"""Reproduce aula4 pp.97/99 as an explicitly descriptive 100+100 exercise.

Labels mean payment to the course address versus unattributed background.
They are not verified theft or hardware-wallet labels. Existing models are untouched.
"""
import argparse
import csv
import hashlib
import heapq
import json
import math
from collections import Counter
from pathlib import Path
import statistics

import numpy as np
import sklearn
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

from audit_coldcard_parents import transactions, SEEDS

TARGET = 'bc1qnk4zh9qcnap2mycp56qjrgza3cc8ylrh8fecp0'
FEATURES = ['size_bytes', 'weight_wu', 'fee_sat', 'output_sum_sat',
            'output_min_sat', 'output_max_sat', 'output_mean_sat',
            'output_std_sat', 'input_count', 'output_count']


def row_from_tx(height, tx):
    previous = [i.get('prev_out') or {} for i in tx['inputs']]
    if (len(previous) == 1 and previous[0].get('tx_index') == 0
            and previous[0].get('n') == 4294967295):
        return None
    amounts = [o['value'] for o in tx['out']]
    if not amounts or any(v < 0 for v in amounts):
        raise ValueError('Invalid output amounts')
    features = [tx['size'], tx['weight'], tx['fee'], sum(amounts), min(amounts),
                max(amounts), statistics.mean(amounts), statistics.pstdev(amounts),
                len(previous), len(amounts)]
    if not all(math.isfinite(v) and v >= 0 for v in features):
        raise ValueError('Invalid feature')
    return dict(txid=tx['hash'], block_height=height,
                pays_course_address=any(o.get('addr') == TARGET for o in tx['out']),
                **dict(zip(FEATURES, features)))


def rank(txid):
    return int.from_bytes(hashlib.sha256(('42:' + txid).encode()).digest(), 'big')


def keep_smallest(heap, row, count=100):
    item = (-rank(row['txid']), row['txid'], row)
    if len(heap) < count:
        heapq.heappush(heap, item)
    elif item[0] > heap[0][0]:
        heapq.heapreplace(heap, item)


def choose_cohort(positives, background, count=100):
    if len(positives) < count:
        raise ValueError('Fewer than 100 course-address payments in supplied data')
    selected = sorted(positives, key=lambda r: rank(r['txid']))[:count]
    needed = Counter(r['block_height'] for r in selected)
    for height, n in sorted(needed.items()):
        pool = sorted((item[2] for item in background.get(height, [])),
                      key=lambda r: rank(r['txid']))
        if len(pool) < n:
            raise ValueError('Insufficient same-block background')
        selected.extend(pool[:n])
    if len({r['txid'] for r in selected}) != count * 2:
        raise ValueError('Duplicate or overlapping cohort')
    return sorted(selected, key=lambda r: r['txid'])


def run(archive, parents_path, output):
    if output.exists():
        raise ValueError('Output directory must be new')
    parents_bytes = parents_path.read_bytes()
    parents = json.loads(parents_bytes)
    candidate_ids = {r['txid'] for r in parents['parents']}
    excluded_background = candidate_ids | SEEDS
    positives, background, seen = [], {}, set()
    row_count = 0
    for height, tx in transactions(archive):
        row_count += 1
        if tx['hash'] in seen:
            raise ValueError('Duplicate transaction in archive')
        seen.add(tx['hash'])
        row = row_from_tx(height, tx)
        if row is None:
            continue
        if row['pays_course_address']:
            positives.append(row)
        elif tx['hash'] not in excluded_background:
            keep_smallest(background.setdefault(height, []), row)
    if row_count != 493571 or candidate_ids - seen or SEEDS - seen:
        raise ValueError('Unexpected archive coverage')
    rows = choose_cohort(positives, background)
    x = np.array([[r[f] for f in FEATURES] for r in rows], dtype=float)
    y = np.array([int(r['pays_course_address']) for r in rows])
    train, test = train_test_split(np.arange(len(rows)), test_size=.30,
                                   stratify=y, random_state=42)
    model = DecisionTreeClassifier(max_depth=4, min_samples_leaf=5, random_state=42)
    model.fit(x[train], y[train])
    pred = model.predict(x[test])
    precision, recall, f1, _ = precision_recall_fscore_support(
        y[test], pred, average='binary', zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y[test], pred, labels=[0, 1]).ravel()
    output.mkdir(parents=True)
    with (output / 'cohort.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) + ['split'])
        writer.writeheader()
        training = set(train)
        writer.writerows(dict(r, split='train' if i in training else 'test')
                         for i, r in enumerate(rows))
    (output / 'tree.txt').write_text(export_text(model, feature_names=FEATURES, decimals=5))

    # Apply the already fitted classroom tree to unused unattributed transactions.
    # Candidate destinations are review leads, not newly established case labels.
    cohort_ids = {r['txid'] for r in rows}
    destinations, pending = {}, []
    scanned = alerts = 0

    def flush():
        nonlocal scanned, alerts
        if not pending:
            return
        features = np.array([[r[f] for f in FEATURES] for r, _ in pending], dtype=float)
        predictions = model.predict(features)
        scores = model.predict_proba(features)[:, 1]
        scanned += len(pending)
        for (r, outs), flag, score in zip(pending, predictions, scores):
            if not flag:
                continue
            alerts += 1
            per_address = Counter()
            for out in outs:
                if out.get('addr') and out['addr'] != TARGET:
                    per_address[out['addr']] += out['value']
            for address, amount in per_address.items():
                item = destinations.setdefault(address, dict(address=address,
                    flagged_transaction_count=0, gross_outputs_sat=0,
                    max_classroom_leaf_fraction=0., example_txids=[]))
                item['flagged_transaction_count'] += 1
                item['gross_outputs_sat'] += amount
                item['max_classroom_leaf_fraction'] = max(
                    item['max_classroom_leaf_fraction'], float(score))
                if len(item['example_txids']) < 3:
                    item['example_txids'].append(r['txid'])
        pending.clear()

    for height, tx in transactions(archive):
        if tx['hash'] in cohort_ids or tx['hash'] in candidate_ids or tx['hash'] in SEEDS:
            continue
        row = row_from_tx(height, tx)
        if row is None or row['pays_course_address']:
            continue
        pending.append((row, tx['out']))
        if len(pending) >= 4096:
            flush()
    flush()
    top = sorted(destinations.values(), key=lambda r: (
        -r['flagged_transaction_count'], r['address']))[:20]
    with archive.open('rb') as handle:
        archive_sha = hashlib.file_digest(handle, 'sha256').hexdigest()
    report = dict(status='executed_classroom_proxy_exercise',
        source='aula4.pdf, 24 September 2026, pages 97 and 99',
        course_address=TARGET, archive_sha256=archive_sha,
        parents_sha256=hashlib.sha256(parents_bytes).hexdigest(),
        archive_transaction_count=row_count, course_address_payment_count=len(positives),
        features=FEATURES, output_std_definition='population standard deviation, ddof=0',
        sampling='100 payments ranked by SHA256(42:txid), 100 unattributed rows matched by block',
        train_count=len(train), test_count=len(test), train_positive_count=int(y[train].sum()),
        test_positive_count=int(y[test].sum()),
        settings=dict(max_depth=4, min_samples_leaf=5, random_state=42),
        sklearn_version=sklearn.__version__,
        held_out_sample_proxy_metrics=dict(true_negative=int(tn), false_positive=int(fp),
            false_negative=int(fn), true_positive=int(tp), precision=float(precision),
            recall=float(recall), f1=float(f1)),
        review_scan=dict(unused_unattributed_transactions=scanned, flagged_transactions=alerts,
            distinct_output_addresses=len(destinations), top_destinations=top),
        limitations=[
            'Training and sample test share one address, incident and blocks; no independent case validation',
            'Balanced classroom prevalence cannot estimate deployment precision',
            'Background is unattributed, not verified legitimate',
            'Features v are interpreted as output values; the course slide does not explicitly define v',
            'Tree hyperparameters are fixed implementation choices, not specified in the slide',
            'Review leads are gross outputs of flagged transactions, not stolen balances or actor identities',
            'Leaf fractions are not calibrated theft probabilities; no external evidence confirms review leads'])
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('course_address_payment_count',
        'held_out_sample_proxy_metrics')}))
    print(json.dumps(dict(scanned=scanned, flags=alerts, review_destinations=len(destinations))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    parser.add_argument('parents', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    run(args.archive, args.parents, args.output)
