"""Independent standard-library checks of the prepared scope and recovered bytes.

No collector, feature extractor, ML package or HTTP client is imported.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

OUT = Path(__file__).resolve().parent
BASE = OUT.parent


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify(primary, restored, work):
    protocol = read(OUT/'protocol.json')
    audit = read(OUT/'capacity_and_cache_audit.json')
    receipt = read(OUT/'resume_checkpoint.json')
    previous = BASE/'source_prefix_extension_20261109_01'
    backup = read(previous/'private_cache_backup.json')
    primary_archive = primary.parent/backup['file_name']
    assert primary_archive.stat().st_size == backup['bytes']
    assert sha(primary_archive) == backup['sha256']
    with tarfile.open(primary_archive) as archive:
        assert archive.extractfile('PRIVATE_CACHE_MANIFEST.json').read() == (primary/'PRIVATE_CACHE_MANIFEST.json').read_bytes()
    files = read(primary/'PRIVATE_CACHE_MANIFEST.json')['entries']
    for entry in files:
        path = (primary/entry['path']).resolve()
        assert path.is_relative_to(primary) and path.stat().st_size == entry['bytes']
        assert sha(path) == entry['sha256']
    for pin in protocol['inputs'].values():
        assert sha((OUT/pin['file']).resolve()) == pin['sha256'], pin['file']
    inherited = read(previous/'protocol.json')['inputs'].values()
    current_pins = {((OUT/p['file']).resolve(), p['sha256']) for p in protocol['inputs'].values()}
    assert {((previous/p['file']).resolve(), p['sha256']) for p in inherited} <= current_pins
    assert len(protocol['inputs']) == audit['total_published_input_pins']
    assert sha(OUT/'protocol.json') == receipt['protocol_sha256']
    plan = read(work/'plan.json')
    assert sha(work/'plan.json') == protocol['private_plan_sha256']
    assert sha(work/'historical_locks.json') == protocol['private_lock_manifest_sha256']
    ids = protocol['source_ids']
    prior_resume = read(previous/'resume_checkpoint.json')
    assert ids == prior_resume['next_extension_source_ids'] == [r['pilot_id'] for r in plan]
    assert not set(ids) & set(prior_resume['source_ids'])
    rows = {r['source_id']: r for r in read(previous/'precutoff_feature_view.json.gz')['rows']}
    assert sum(r['features'] is not None for r in rows.values()) == 1382
    reused = read(OUT/'offline_reuse_manifest.json')['responses']
    assert len(reused) == 177 == protocol['offline_reused_responses']
    assert len(list((work/'requests').glob('*/*.json'))) == len(reused)
    tails = references = 0
    for record in plan:
        sid = record['pilot_id']
        assert rows[sid]['features'] is None
        for field in ('address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash'):
            assert record[field] == rows[sid][field]
        own = [m for m in reused if m['source_id'] == sid]
        if not own:
            continue
        metas = {m['key']: m for m in own}
        assert 'reference' in metas
        tail_keys = sorted(k for k in metas if k.startswith('tail_'))
        assert tail_keys == ['tail_%04d' % i for i in range(len(tail_keys))]
        references += 1
        cursor = record['payment_txid']
        for key in ['reference'] + tail_keys:
            body = work/'requests'/sid/(key+'.json.gz')
            marker = read(work/'requests'/sid/(key+'.json'))
            assert sha(body) == metas[key]['sha256'] == marker['sha256']
            assert marker['http_status'] == 200 and marker['offline_reused'] is True
            assert 'error_type' not in marker
            endpoint = ('/tx/'+record['payment_txid'] if key == 'reference' else
                        '/address/'+record['address']+'/txs/chain/'+cursor)
            assert hashlib.sha256(endpoint.encode()).hexdigest() == metas[key]['endpoint_sha256'] == marker['endpoint_sha256']
            payload = read(body)
            if key.startswith('tail_'):
                assert 0 < len(payload) <= 25
                assert all(t['status']['confirmed'] and t['status']['block_hash'] and
                           t['status']['block_height'] <= record['cutoff_height'] for t in payload)
                cursor = payload[-1]['txid']
                tails += 1
    assert tails == 166 and references == 11
    budget = protocol['request_budget']
    assert budget == dict(ordinary_counter_gets=1, new_reference_gets_at_most=9,
        new_tail_pages_at_most=474, fresh_reference_statuses_at_most=20,
        funding_status_gets_at_most=21, total_new_requests_at_most=525)
    assert not list((work/'results').iterdir()) and not list((work/'raw').iterdir())
    assert not (work/'lease_published').exists()
    assert receipt['status'] == 'prepared_offline_not_started'
    assert receipt['provider_requests'] == receipt['model_fits'] == 0

    public = BASE/'reference_tail_continuation_20261102_1508'
    entries = read(public/'checkpoint.json.gz')['entries']
    response_manifest = read(public/'request_manifest.json.gz')
    for entry in entries.values():
        assert sha(restored/entry['raw_file']) == entry['raw_sha256']
    for meta in response_manifest:
        assert sha(restored/'requests'/meta['source_id']/(meta['key']+'.json.gz')) == meta['sha256']
    restoration = read(OUT/'cache_restoration_verification.json')
    assert restoration['supplemental_archive']['container_verified'] is False
    assert restoration['reconstructed_responses_individually_verified'] == len(response_manifest) == 332
    assert restoration['recovered_raw_tails'] == len(entries) == 19
    public_text = '\n'.join(p.read_text() for p in OUT.iterdir() if p.suffix in ('.py', '.json', '.md'))
    for record in plan:
        assert record['address'] not in public_text and record['payment_txid'] not in public_text
    assert str(primary.parent.parent) not in public_text
    result = dict(schema_version=1, status='passed', primary_archive_sha256_verified=backup['sha256'],
        primary_private_files_verified=len(files), protocol_input_pins_verified=len(protocol['inputs']),
        fixed_selected_sources_verified=len(plan), saved_response_bodies_verified=len(reused),
        contiguous_tail_pages_verified=tails, recovered_raw_tails_verified=len(entries),
        reconstructed_response_bodies_verified=len(response_manifest), request_budget_verified=525,
        public_selected_identifiers_redacted=True, provider_requests=0, model_fits=0,
        new_feature_vectors=0, prepared_scope_not_started=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('primary', 'restored', 'work'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    result = verify(args.primary.resolve(), args.restored.resolve(), args.work.resolve())
    path = OUT/'independent_preparation_verification.json'
    if path.exists():
        raise FileExistsError('Do not overwrite a verification receipt')
    path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
