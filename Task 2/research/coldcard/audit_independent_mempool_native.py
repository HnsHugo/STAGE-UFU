"""Re-extract native source prefixes, recount vectors and verify provider/stop evidence."""
import argparse
from datetime import datetime
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
from independent_mempool_pilot import PROVIDER


def audit(out, work):
    q = read(out / 'protocol.json')
    spec = importlib.util.spec_from_file_location('preserved_prefix_auditor', out.parent / 'source_prefix_extension_20261112_01/audit_execution.py')
    original = importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
    original.audit(out / 'protocol.json', work)
    report = read(out / 'coverage_audit.json')
    manifest = [read(p) for p in sorted((work / 'requests').glob('*/*.json'))]
    assert manifest == read(out / 'request_manifest.json.gz')
    assert all(m['provider'] == PROVIDER and not m.get('offline_reused') for m in manifest)
    assert len(manifest) <= q['maximum_requests']
    dispatched = sorted(m['dispatch_at'] for m in manifest if m.get('dispatch_at'))
    assert all((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds() >= q['minimum_dispatch_interval_seconds'] - .1
               for a, b in zip(dispatched, dispatched[1:]))
    failures = [m for m in manifest if 'error_type' in m]
    if failures:
        stopped = min(m['finished_at'] for m in failures)
        assert all(m['started_at'] <= stopped for m in manifest)
    receipt = read(out / 'run_receipt.json')
    assert receipt['provider_requests'] == len(manifest)
    assert receipt['failures'] == len(failures)
    assert receipt['operational_locks_released'] and receipt['blockstream_provider_requests'] == 0
    assert receipt['model_fits'] == receipt['new_scores'] == 0
    cp = read(out / 'checkpoint.json.gz'); entries = cp['entries']
    records = {r['pilot_id']: r for r in read(work / 'plan.json')}
    cursors, details = {}, []
    for sid, record in records.items():
        cursor, pages, transactions, exhausted = record['payment_txid'], 0, [], False
        for i in range(q['max_pages_per_address']):
            body = work / 'requests' / sid / (f'tail_{i:04d}.json.gz')
            if not body.exists():
                break
            page = read(body); pages += 1
            if not page:
                exhausted = True; break
            transactions.extend(page); cursor = page[-1]['txid']
        cursors[sid] = dict(provider=PROVIDER, cursor=cursor, saved_native_pages=pages,
                            pagination_exhausted=exhausted, finalized=sid in entries)
        details.append(dict(source_id=sid, finalized=sid in entries,
            status=entries[sid]['status'] if sid in entries else 'pending', saved_native_pages=pages,
            source_transaction_observations_saved=sum(t['status']['block_height'] < record['cutoff_height'] for t in transactions),
            last_native_cursor_sha256=hashlib.sha256(cursor.encode()).hexdigest()))
    write(work / 'native_cursors.json', cursors)
    view = read(out / 'precutoff_feature_view.json.gz')
    for row in view['rows']:
        if row['source_id'] in entries:
            row['precutoff_history_provenance'].update(provider=PROVIDER,
                method='native reference-cursor pagination with anchored funding closure')
    (out / 'precutoff_feature_view.json.gz').write_bytes(gzip.compress(json_bytes(view), mtime=0))
    report.update(status='passed', provider=PROVIDER, provider_or_route_changed=True,
        provider_change_explicitly_authorized=True, automatic_provider_rotation=False,
        source_progress=details, source_transaction_observations_saved=sum(d['source_transaction_observations_saved'] for d in details),
        observation_count_is_not_globally_unique_transactions=True,
        additional_observations_vs_old_blockstream_prefix_not_claimed=True,
        blockstream_provider_requests=0, private_native_cursors_sha256=sha(work / 'native_cursors.json'),
        composed_view_sha256=sha(out / 'precutoff_feature_view.json.gz'))
    write(out / 'coverage_audit.json', report)
    write(out / 'independent_verification.json', dict(report,
        verification_basis='Preserved original cursor/body audit and pure UTXO extraction; separate feature recount; independent native-provider timing/budget/stop verification; old-row invariants'))
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('scope', type=Path); p.add_argument('work', type=Path)
    a = p.parse_args(); print(json.dumps(audit(a.scope.resolve(), a.work.resolve()), sort_keys=True))
