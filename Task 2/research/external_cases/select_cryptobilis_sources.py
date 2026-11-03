"""Complete anchored input census and frozen CryptoBilis comparison selection.

Selection uses no history availability, feature or model score. Raw blocks and
the decoded execution plan stay private; the hashed census replays the sample.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import json
from pathlib import Path
import sys

import build_cryptobilis_source_protocol as ready

ROOT = ready.ROOT
sys.path.insert(0, str(ROOT/'coldcard'))
from source_comparison_design import census
from source_cohort import atomic_write


def case_plan(configuration):
    config = ready.read(configuration)
    paths = {k: ready.pinned(v) for k, v in config['inputs'].items()}
    central = ready.read(paths['central'])
    refs = [r for r in central['references'] if r['case_group'] == 'cryptobilis_2026']
    blocks = [b for b in central['blocks'] if b['case_group'] == 'cryptobilis_2026']
    histories = {ready.read(paths['collector_'+str(i)])['address']:
                 ready.read(paths['collector_'+str(i)]) for i in range(2)}
    start = int(ready.datetime.fromisoformat(config['event_window']['start_utc']).timestamp())
    end = int(ready.datetime.fromisoformat(config['event_window']['end_exclusive_utc']).timestamp())
    rows, _, _, _ = ready.recover(histories, refs, blocks, start, end)
    ready.require(rows == ready.read(configuration.parent/'source_registry.json.gz')['rows'],
                  'Recovered cases differ from the saved registry')
    transactions = {ready.hashed(t['txid']): t for h in histories.values() for t in h['transactions']}
    addresses = {ready.hashed(v['prevout']['scriptpubkey_address']): v['prevout']['scriptpubkey_address']
                 for t in transactions.values() for v in t['vin'] if v.get('prevout')}
    records = []
    for row in rows:
        tx = transactions[row['reference_txid_sha256']]
        address = addresses[row['address_sha256']]
        own = [v for v in tx['vin'] if v['prevout']['scriptpubkey_address'] == address]
        records.append(dict(pilot_id=row['source_id'], address=address,
                            address_sha256=row['address_sha256'], payment_txid=tx['txid'],
                            payment_txid_sha256=row['reference_txid_sha256'],
                            cutoff_height=row['cutoff_height'], cutoff_block_hash=row['cutoff_block_hash'],
                            registry_input_slots=len(own),
                            reference_input_value_sat=sum(v['prevout']['value'] for v in own)))
    return records, rows


def choose(first, contract):
    excluded = set(contract['excluded_address_sha256'])
    selected, strata = [], []
    for quota in contract['quotas']:
        pool = [r for a, r in first.items() if ready.hashed(a) not in excluded
                and r['cutoff_height'] == quota['height']]
        pool.sort(key=lambda r: (ready.hashed(contract['salt']+r['address']), r['address']))
        take = pool[:quota['desired_comparisons']]
        selected.extend(take)
        strata.append(dict(height=quota['height'], eligible_sources=len(pool),
                           quota=quota['desired_comparisons'], selected=len(take),
                           shortfall=max(0, quota['desired_comparisons']-len(take))))
    return selected, strata


def replay(public, contract):
    rows = public['sources']
    ready.require(len({r['address_sha256'] for r in rows}) == len(rows), 'Repeated hashed census source')
    ready.require(len({r['selection_key'] for r in rows}) == len(rows), 'Selection hash tie needs raw tie audit')
    excluded = set(contract['excluded_address_sha256'])
    ready.require(all(r['excluded'] == (r['address_sha256'] in excluded) for r in rows), 'Changed exclusion flag')
    selected = []
    for q in contract['quotas']:
        pool = sorted((r for r in rows if not r['excluded'] and r['cutoff_height'] == q['height']),
                      key=lambda r: r['selection_key'])
        selected.extend(pool[:q['desired_comparisons']])
    return [r['address_sha256'] for r in selected]


def execution_order(records, rows):
    by_id = {r['pilot_id']: r for r in records}
    order = []
    for height in sorted({r['cutoff_height'] for r in rows}):
        cases = sorted(r['source_id'] for r in rows if r['cutoff_height'] == height
                       and r['cryptobilis_reference_source_membership'] == 1)
        controls = sorted(r['source_id'] for r in rows if r['cutoff_height'] == height
                          and r['cryptobilis_reference_source_membership'] == 0)
        for offset in range(max(len(cases), (len(controls)+1)//2)):
            order += cases[offset:offset+1] + controls[2*offset:2*offset+2]
    ready.require(len(order) == len(by_id) == len(set(order)), 'Execution order lost/repeated a source')
    return [by_id[key] for key in order]


def select(configuration, cache, output, work):
    contract_path = configuration.parent/'transfer_protocol.json'
    transfer = ready.read(contract_path)
    records, cases = case_plan(configuration)
    blocks, snapshots = [], []
    for ref in transfer['blocks']:
        path = cache/(str(ref['height'])+'.json')
        raw = path.read_bytes()
        blocks.append(json.loads(raw))
        snapshots.append(dict(height=ref['height'], sha256=ready.sha(raw), bytes=len(raw)))
    first, transactions, stats = census(blocks, transfer['blocks'])
    for r in records:
        height, tx = transactions[r['payment_txid']]
        own = [i['prev_out'] for i in tx['inputs'] if (i.get('prev_out') or {}).get('addr') == r['address']]
        ready.require(height == r['cutoff_height'] and len(own) == r['registry_input_slots']
                      and sum(v['value'] for v in own) == r['reference_input_value_sat'],
                      'Case reference/input value/count differs across providers')
    chosen, strata = choose(first, transfer['comparison_selection'])
    rows = deepcopy(cases)
    for i, r in enumerate(chosen, 1):
        source_id = f'cryptobilis_comparison_{i:04d}'
        _, tx = transactions[r['reference_txid']]
        own = [v['prev_out'] for v in tx['inputs'] if (v.get('prev_out') or {}).get('addr') == r['address']]
        records.append(dict(pilot_id=source_id, address=r['address'], address_sha256=ready.hashed(r['address']),
                            payment_txid=r['reference_txid'], payment_txid_sha256=ready.hashed(r['reference_txid']),
                            cutoff_height=r['cutoff_height'], cutoff_block_hash=r['cutoff_block_hash'],
                            registry_input_slots=len(own), reference_input_value_sat=sum(v['value'] for v in own)))
        rows.append(dict(source_id=source_id, address_sha256=ready.hashed(r['address']),
                         reference_txid_sha256=ready.hashed(r['reference_txid']),
                         cutoff_height=r['cutoff_height'], cutoff_block_hash=r['cutoff_block_hash'],
                         incident_group='cryptobilis_2026', case_relation='same_block_unattributed_comparison',
                         cryptobilis_reference_source_membership=0, labels=deepcopy(cases[0]['labels']),
                         features=None, prior_prefix_status='not_collected_in_this_unit'))
    ready.require(len({r['address_sha256'] for r in rows}) == len(rows), 'Case/comparison identity overlap')
    excluded = set(transfer['comparison_selection']['excluded_address_sha256'])
    public = dict(schema_version=1, transfer_protocol_sha256=ready.sha(contract_path.read_bytes()),
                  snapshots=snapshots, blocks=transfer['blocks'], census=stats,
                  sources=sorted([dict(address_sha256=ready.hashed(a),
                      reference_txid_sha256=ready.hashed(r['reference_txid']),
                      cutoff_height=r['cutoff_height'], cutoff_block_hash=r['cutoff_block_hash'],
                      selection_key=ready.hashed(transfer['comparison_selection']['salt']+a),
                      excluded=ready.hashed(a) in excluded) for a, r in first.items()],
                      key=lambda r:r['address_sha256']))
    ready.require(replay(public, transfer['comparison_selection']) == [ready.hashed(r['address']) for r in chosen],
                  'Hashed census replay differs from raw selection')
    plan = execution_order(records, rows)
    summary = dict(schema_version=1, cases=len(cases), comparisons=len(chosen),
                   complete_blocks=len(blocks), block_transactions=sum(s['transaction_count'] for s in stats),
                   unique_decoded_positive_input_sources=len(first), strata=strata,
                   census=stats, case_reference_inputs_reconciled=len(records)-len(chosen),
                   source_vectors_available=0, scores_computed=0, model_fits=0,
                   private_plan_sha256=ready.sha(ready.encoded(plan)),
                   transfer_protocol_sha256=ready.sha(contract_path.read_bytes()),
                   execution_order='Block height; round-robin one source-ID-sorted case and two source-ID-sorted comparisons; no outcome-dependent reordering.',
                   case_relation='graph_candidate', verified_compromise_or_device_labels=0,
                   history_collection_performed=False, cryptographic_inclusion_verified=False)
    output.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    files={'input_census.json.gz':gzip.compress(ready.encoded(public),mtime=0),
           'source_selection.json.gz':gzip.compress(ready.encoded(dict(schema_version=1,rows=rows)),mtime=0),
           'selection_audit.json':ready.encoded(summary)}
    for name, raw in files.items():
        ready.require(not (output/name).exists(), 'Selection output already exists')
        atomic_write(output/name, raw)
    atomic_write(work/'plan.json', ready.encoded(plan))
    atomic_write(output/'selection_verification.json',ready.encoded(dict(
        hashed_census_replay_exact=True, cases_recovered_exactly=True,
        all_122_cross_provider_input_anchors_agree=True,
        outputs_sha256={k:ready.sha(v) for k,v in files.items()},
        raw_blocks_private=True, model_and_labels_unchanged=True)))
    return summary


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('configuration',type=Path); p.add_argument('cache',type=Path)
    p.add_argument('output',type=Path); p.add_argument('work',type=Path)
    a=p.parse_args()
    print(json.dumps(select(a.configuration.resolve(),a.cache,a.output,a.work)))
