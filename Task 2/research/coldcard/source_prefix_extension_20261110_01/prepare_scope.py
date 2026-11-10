"""Prepare the next fixed 20-source extension without provider traffic or fitting."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
sys.path.insert(0, str(BASE))
from build_source_registry import json_bytes
import collect_reference_tail as tail
from recover_cache import read, require, sha, records_from_primary


def validate_cached(record, work, max_pages=16):
    """Return only a contiguous, anchored, independently fingerprinted prefix."""
    folder = work / 'requests' / record['pilot_id']
    cursor, previous = record['payment_txid'], record['cutoff_height']
    seen, accepted = set(), []
    for key in ['reference'] + ['tail_%04d' % i for i in range(max_pages)]:
        marker, body = folder / (key + '.json'), folder / (key + '.json.gz')
        if not marker.exists() or not body.exists():
            break
        meta = read(marker)
        if meta.get('http_status') != 200 or 'error_type' in meta:
            break
        endpoint = ('/tx/' + record['payment_txid'] if key == 'reference' else
                    '/address/' + record['address'] + '/txs/chain/' + cursor)
        require(meta['source_id'] == record['pilot_id'] and meta['key'] == key,
                'Cached response/source key differs')
        require(sha(body) == meta['sha256'], 'Cached response fingerprint differs')
        require(hashlib.sha256(endpoint.encode()).hexdigest() == meta['endpoint_sha256'],
                'Cached endpoint/cursor sequence differs')
        data = read(body)
        if key == 'reference':
            tail.anchor_check(record, data)
        else:
            require(isinstance(data, list) and 0 < len(data) <= 25,
                    'An exhausted prefix must be audited before extension')
            for tx in data:
                require(tx['txid'] != record['payment_txid'] and tx['txid'] not in seen,
                        'Repeated cached cursor transaction')
                status = tx['status']
                require(status.get('confirmed') is True and status.get('block_hash') and
                        status['block_height'] <= previous, 'Unanchored/unordered cached page')
                previous = status['block_height']
                seen.add(tx['txid'])
            cursor = data[-1]['txid']
        accepted.append((key, marker, body, meta))
    return accepted


def choose_sources(resume, view):
    ids = resume['next_extension_source_ids']
    require(0 < len(ids) <= 20 and len(set(ids)) == len(ids), 'Invalid next fixed selection')
    require(ids == sorted(resume['coldcard_unextended_at_16_page_bound_source_ids'])[:20],
            'Selection differs from the declared next unextended IDs')
    rows = {r['source_id']: r for r in view['rows']}
    require(not set(ids) & set(resume['source_ids']), 'Closed extension selected again')
    require(all(rows[sid]['features'] is None for sid in ids), 'Complete prefix selected')
    return ids, rows


def prepare(primary, restored, work):
    predecessor = BASE / 'source_prefix_extension_20261109_01'
    require(not (OUT / 'protocol.json').exists() and not work.exists(), 'Never overwrite a prepared scope')
    resume_path = predecessor / 'resume_checkpoint.json'
    resume = read(resume_path)
    baseline_path = predecessor / 'precutoff_feature_view.json.gz'
    view = read(baseline_path)
    ids, rows = choose_sources(resume, view)
    require(resume['network_source_ids'] == [] and not resume['collection_can_resume'],
            'Predecessor is not a closed scope')
    records = records_from_primary(primary)
    selected = [records[sid] for sid in ids]
    for record in selected:
        for key in ('address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash'):
            require(record[key] == rows[record['pilot_id']][key], 'Frozen source identity differs')
        require(hashlib.sha256(record['address'].encode()).hexdigest() == record['address_sha256'] and
                hashlib.sha256(record['payment_txid'].encode()).hexdigest() == record['payment_txid_sha256'],
                'Private plan identifiers do not match their fingerprints')
    prior_proto = read(predecessor / 'protocol.json')
    inputs = {}
    for name, pin in prior_proto['inputs'].items():
        path = (predecessor / pin['file']).resolve()
        require(sha(path) == pin['sha256'], 'Published predecessor pin differs')
        inputs[name] = dict(file=os.path.relpath(path, OUT), sha256=pin['sha256'])
    for name, path in dict(predecessor_protocol=predecessor/'protocol.json',
        predecessor_checkpoint=predecessor/'checkpoint.json.gz', predecessor_resume=resume_path,
        baseline_view=baseline_path, predecessor_audit=predecessor/'coverage_audit.json',
        predecessor_stop=predecessor/'collection_stop.json', predecessor_requests=predecessor/'request_manifest.json.gz',
        predecessor_backup=predecessor/'private_cache_backup.json', preparation_code=Path(__file__),
        restoration_code=OUT/'recover_cache.py', restoration_report=OUT/'cache_restoration_verification.json').items():
        inputs[name] = dict(file=os.path.relpath(path, OUT), sha256=sha(path))
    candidates = sorted({p.parent for p in primary.rglob('plan.json')} | {restored})
    work.mkdir(parents=True)
    for name in ('requests', 'raw', 'results'):
        (work/name).mkdir()
    (work/'plan.json').write_bytes(json_bytes(selected))
    (work/'preflight.json').write_bytes(json_bytes(selected[0]))
    # Lock every restored historical work folder and any local canonical folder.
    locks = sorted({str(p/'collector.lock') for p in candidates} |
                   {str(p/'collector.lock') for p in BASE.glob('source_cohort_work_*') if p.is_dir() and p != work})
    (work/'historical_locks.json').write_bytes(json_bytes(locks))
    reused, per_source, tail_pages, references = [], [], 0, 0
    for record in selected:
        options = [(validate_cached(record, candidate), candidate) for candidate in candidates]
        accepted, candidate = max(options, key=lambda item: len(item[0]))
        folder = work/'requests'/record['pilot_id']
        folder.mkdir()
        for key, marker, body, meta in accepted:
            origin = meta.get('reused_from_pass', candidate.name.removeprefix('source_cohort_work_'))
            (folder/body.name).write_bytes(body.read_bytes())
            (folder/marker.name).write_bytes(json_bytes(dict(meta, offline_reused=True, reused_from_pass=origin)))
            reused.append(dict(source_id=record['pilot_id'], key=key, predecessor_pass=origin,
                               sha256=meta['sha256'], endpoint_sha256=meta['endpoint_sha256']))
        pages = sum(key.startswith('tail_') for key, *_ in accepted)
        tail_pages += pages
        references += bool(accepted)
        per_source.append(dict(source_id=record['pilot_id'], verified_saved_tail_pages=pages,
                               verified_saved_reference=bool(accepted), new_tail_pages_at_most=32-pages))
    (OUT/'offline_reuse_manifest.json').write_bytes(json_bytes(dict(schema_version=1, responses=reused)))
    all_restored = {p.name for p in (restored/'requests').iterdir()}
    report = dict(schema_version=1, scope='offline_preparation_only', selected_source_ids=ids,
        sources=len(ids), sources_with_saved_reference=references, saved_tail_pages_reused=tail_pages,
        saved_responses_reused=len(reused), per_source=per_source,
        additional_restored_bounded_sources=len(all_restored & set(resume['coldcard_remaining_bounded_source_ids'])),
        predecessor_input_pins_verified=len(prior_proto['inputs']),
        total_published_input_pins=len(set(inputs) | {'successor_offline_reuse_manifest', 'capacity_and_cache_audit'}),
        request_budget=dict(ordinary_counter_gets=1, new_reference_gets_at_most=len(ids)-references,
            new_tail_pages_at_most=32*len(ids)-tail_pages, fresh_reference_statuses_at_most=len(ids),
            funding_status_gets_at_most=sum(r['registry_input_slots'] for r in selected)),
        exact_exhaustion_cost_known=False, selected_coldcard_sources=1500,
        coldcard_vectors_unchanged=sum(r['features'] is not None for r in view['rows']),
        coldcard_bounded_prefixes_unchanged=118, cryptobilis_vectors_unchanged=329,
        total_remaining_bounded_prefixes_unchanged=155, provider_requests=0, model_fits=0,
        new_feature_vectors=0, old_failed_markers_copied=False, old_scope_restarted=False,
        prior_32_page_bounded_sources_excluded=True, full_current_history_statuses_unchanged=True,
        verified_labels_remain_unknown=True)
    budget = report['request_budget']
    budget['total_new_requests_at_most'] = sum(budget.values())
    (OUT/'capacity_and_cache_audit.json').write_bytes(json_bytes(report))
    for name in ('offline_reuse_manifest', 'capacity_and_cache_audit'):
        path = OUT/(name+'.json')
        key = 'successor_offline_reuse_manifest' if name == 'offline_reuse_manifest' else name
        inputs[key] = dict(file=path.name, sha256=sha(path))
    proto = dict(prior_proto, pass_name=OUT.name, created_on='2026-11-10', inputs=inputs,
        source_ids=ids, baseline_vectors=report['coldcard_vectors_unchanged'],
        all_gap_targets=dict(coldcard=118, cryptobilis=37, total=155),
        authorization='Hugo requests resumption of STAGE-UFU on 10 November 2026; latest alignment selects this distinct fixed successor.',
        coverage_scope='Distinct extension for the next 20 previously unextended, unavailable Coldcard prefixes; preserve the closed predecessor and its 16 still-bounded 32-page outcomes.',
        private_plan_sha256=sha(work/'plan.json'), private_lock_manifest_sha256=sha(work/'historical_locks.json'),
        offline_reused_responses=len(reused), request_budget=budget,
        original_private_cache_missing_pages_may_require_fresh_gets=True)
    (OUT/'protocol.json').write_bytes(json_bytes(proto))
    checkpoint = dict(schema_version=1, pass_name=OUT.name, status='prepared_offline_not_started',
        protocol_sha256=sha(OUT/'protocol.json'), network_source_ids=ids, source_ids=ids,
        finalized_source_ids=[], provider_requests=0, model_fits=0, collection_can_resume=False,
        collection_requires_fresh_live_lease_and_locks=True, automation_enabled=False,
        coldcard_vectors_available=1382, cryptobilis_vectors_available=329,
        total_remaining_bounded_prefixes=155, historical_results_preserved=True,
        next_action='Hold all historical/local locks, fetch the live published policy, check due time and competing leases, publish/read back a fresh running lease, then permit exactly one original-route counter GET. HTTP200 alone permits this bounded scope; stop at first refusal with no fallback.')
    (OUT/'resume_checkpoint.json').write_bytes(json_bytes(checkpoint))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('primary', 'restored', 'work'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.primary.resolve(), args.restored.resolve(), args.work.resolve()), sort_keys=True))
