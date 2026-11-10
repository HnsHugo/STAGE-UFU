"""Recover individually pinned evidence from a truncated private archive, offline.

The container is never declared verified. Only complete raw members matching
the published checkpoint are accepted; every reconstructed response must also
match its own published compressed-body and endpoint fingerprints.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tarfile

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from build_source_registry import json_bytes
import collect_reference_tail as tail

PASS = 'reference_tail_continuation_20261102_1508'
ARCHIVE_ROOT = 'source_cohort_work_' + PASS


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def complete_members(archive):
    """Yield complete regular members; a partial member is never yielded."""
    with tarfile.open(archive, mode='r|gz') as stream:
        for member in stream:
            name = Path(member.name)
            require(not name.is_absolute() and '..' not in name.parts,
                    'Unsafe archive path')
            require(member.isfile() or member.isdir(), 'Unsupported archive member')
            if member.isfile():
                data = stream.extractfile(member).read()
                require(len(data) == member.size, 'Incomplete member bytes')
                yield member.name, data


def records_from_primary(primary):
    plan = primary / 'coldcard/source_cohort_work_reference_tail_coverage_20261031_221432/plan.json'
    return {r['pilot_id']: r for r in read(plan)}


def restore(primary, archive, work, report_path):
    require(not work.exists() and not report_path.exists(), 'Never overwrite a restoration')
    manifest_path = primary / 'PRIVATE_CACHE_MANIFEST.json'
    manifest = read(manifest_path)
    backup = read(BASE / 'source_prefix_extension_20261109_01/private_cache_backup.json')
    require(len(manifest['entries']) == backup['private_files_verified'], 'Primary file count differs')
    for entry in manifest['entries']:
        path = primary / entry['path']
        require(path.is_relative_to(primary) and path.is_file(), 'Primary file missing')
        require(path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'],
                'Primary evidence fingerprint differs')

    checkpoint_path = BASE / PASS / 'checkpoint.json.gz'
    requests_path = BASE / PASS / 'request_manifest.json.gz'
    checkpoint = read(checkpoint_path)['entries']
    requests = read(requests_path)
    expected = {ARCHIVE_ROOT + '/' + e['raw_file']: (sid, e)
                for sid, e in checkpoint.items()}
    work.mkdir(parents=True)
    recovered = {}
    completed_members = 0
    omitted_flags = 0
    stream_error = None
    try:
        for name, data in complete_members(archive):
            completed_members += 1
            if Path(name).name in ('collector.lock', 'lease_published'):
                omitted_flags += 1
                continue
            if name not in expected:
                continue
            sid, entry = expected[name]
            require(sid not in recovered, 'Duplicate raw member')
            require(hashlib.sha256(data).hexdigest() == entry['raw_sha256'],
                    'Recovered raw tail differs from published checkpoint')
            path = work / entry['raw_file']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            recovered[sid] = read(path)
    except (EOFError, tarfile.ReadError) as error:
        stream_error = type(error).__name__ + ': ' + str(error)
    require(set(recovered) == set(checkpoint), 'Not all pinned raw tails were recovered')

    records = records_from_primary(primary)
    by_source = {}
    for meta in requests:
        key = (meta['source_id'], meta['key'])
        require(key not in by_source, 'Duplicate public response key')
        by_source[key] = meta
    verified_responses = 0
    endpoint_sequences = 0
    for sid, raw in sorted(recovered.items()):
        record = records[sid]
        require(hashlib.sha256(raw['address'].encode()).hexdigest() == record['address_sha256'],
                'Recovered source identity differs')
        normalized = tail.tail_check(record, raw['anchor'], raw['transactions'],
                                     raw['pagination_exhausted'], raw['anchor_after'],
                                     raw['parent_statuses'])
        require(all(normalized[k] == checkpoint[sid][k]
                    for k in ('status', 'features', 'prefix')), 'Recovered outcome differs')
        transactions = raw['transactions']
        pages = raw['pages_fetched']
        require(0 < pages <= 16 and len(transactions) <= pages * 25, 'Invalid saved page bound')
        payloads = {'reference': (raw['anchor'], '/tx/' + record['payment_txid']),
                    'reference_after': (raw['anchor_after'], '/tx/' + record['payment_txid'] + '/status')}
        cursor = record['payment_txid']
        for index in range(pages):
            page = transactions[index * 25:(index + 1) * 25]
            payloads['tail_%04d' % index] = (page, '/address/' + record['address'] + '/txs/chain/' + cursor)
            if page:
                cursor = page[-1]['txid']
            else:
                require(index == pages - 1 and raw['pagination_exhausted'], 'Unexpected terminal page')
        for txid, status in raw['parent_statuses'].items():
            payloads['parent_' + hashlib.sha256(txid.encode()).hexdigest()] = (status, '/tx/' + txid + '/status')
        require({key for source, key in by_source if source == sid} == set(payloads),
                'Response reconstruction does not cover the public manifest')
        folder = work / 'requests' / sid
        folder.mkdir(parents=True)
        for key, (value, endpoint) in payloads.items():
            meta = by_source[(sid, key)]
            body = gzip.compress(json_bytes(value), mtime=0)
            require(meta.get('http_status') == 200 and 'error_type' not in meta,
                    'Cannot reuse a failed response')
            require(hashlib.sha256(body).hexdigest() == meta['sha256'],
                    'Reconstructed response differs from published fingerprint')
            require(hashlib.sha256(endpoint.encode()).hexdigest() == meta['endpoint_sha256'],
                    'Reconstructed endpoint/cursor sequence differs')
            (folder / (key + '.json.gz')).write_bytes(body)
            (folder / (key + '.json')).write_bytes(json_bytes(dict(
                meta, offline_reused=True, reused_from_pass=PASS,
                recovered_from_individually_pinned_raw_tail=True)))
            verified_responses += 1
            endpoint_sequences += key.startswith('tail_')
    require(verified_responses == len(requests), 'Unaccounted public response')
    contract = read(BASE.parent.parent / 'verification/reference_tail_continuation_20261102.json')['private_evidence_backup']
    report = dict(schema_version=1, scope='offline_private_cache_restoration',
        primary_manifest_sha256=sha(manifest_path), primary_files_verified=len(manifest['entries']),
        supplemental_archive=dict(file_name=archive.name, actual_bytes=archive.stat().st_size,
            actual_sha256=sha(archive), expected_bytes=contract['size_bytes'], expected_sha256=contract['sha256'],
            container_verified=False, stream_error=stream_error, complete_members_read=completed_members),
        operational_flags_omitted=omitted_flags, recovered_raw_tails=len(recovered),
        recovered_complete_prefixes_already_in_baseline=sum(e['status'] == 'complete_prior_prefix' for e in checkpoint.values()),
        recovered_bounded_prefixes=sum(e['status'] == 'bounded_incomplete' for e in checkpoint.values()),
        reconstructed_responses_individually_verified=verified_responses,
        tail_page_endpoint_sequences_verified=endpoint_sequences,
        published_checkpoint_sha256=sha(checkpoint_path), published_request_manifest_sha256=sha(requests_path),
        recovered_source_ids=sorted(recovered), provider_requests=0, model_fits=0,
        new_feature_vectors=0, historical_evidence_overwritten=False)
    report_path.write_bytes(json_bytes(report))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('primary', 'archive', 'work', 'report'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(restore(args.primary.resolve(), args.archive.resolve(),
                             args.work.resolve(), args.report.resolve()), sort_keys=True))
