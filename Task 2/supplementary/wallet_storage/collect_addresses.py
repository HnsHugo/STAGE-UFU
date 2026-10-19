"""Validate a seed CSV and capture resumable WalletExplorer observations."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time
from urllib.error import URLError
from urllib.parse import urlparse

from lookup_address import fetch, normalize

FIELDS = 'address network purpose entity_name entity_source_url entity_evidence storage_type storage_source_url hardware_wallet hardware_source_url illicit_label illicit_source_url reviewed_at_utc notes'.split()
RESULT_FIELDS = FIELDS + ['lookup_status', 'wallet_id', 'service_label', 'updated_to_block',
                         'retrieved_at_utc', 'source_url', 'cached', 'error']


def write_results(path, rows):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def load_seeds(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError('CSV headers must match the documented 14 columns in order')
        rows = list(reader)
    if not rows:
        raise ValueError('CSV contains no addresses')
    seen = set()
    for number, row in enumerate(rows, 2):
        def fail(message):
            raise ValueError(f'CSV row {number}: {message}')
        if None in row or any(value is None for value in row.values()):
            fail('incorrect number of fields')
        if any(value != value.strip() for value in row.values()):
            fail('leading or trailing whitespace')
        address = row['address']
        if not 14 <= len(address) <= 90 or not address.isascii() or not address.isalnum():
            fail('invalid address shape (checksum is not validated)')
        key = (row['network'], address)
        if key in seen:
            fail('duplicate address/network')
        seen.add(key)
        enums = {'network': {'bitcoin_mainnet'},
                 'purpose': {'api_smoke_test', 'research_sample'},
                 'storage_type': {'unknown', 'hot', 'cold'},
                 'illicit_label': {'unknown', 'licit', 'illicit'},
                 'entity_evidence': {'unknown', 'provider_attribution', 'first_party_publication', 'controlled_experiment'}}
        for field, allowed in enums.items():
            if row[field] not in allowed:
                fail(f'invalid {field}')
        for label, source in [('entity_name', 'entity_source_url'), ('storage_type', 'storage_source_url'),
                              ('hardware_wallet', 'hardware_source_url'), ('illicit_label', 'illicit_source_url')]:
            if not row[label]:
                fail(f'{label} must be a value or unknown')
            if row[label] != 'unknown' and not row[source]:
                fail(f'{label} requires {source}')
            if row[source]:
                parsed = urlparse(row[source])
                if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
                    fail(f'{source} must be an HTTP(S) URL')
        if (row['entity_name'] == 'unknown') != (row['entity_evidence'] == 'unknown'):
            fail('entity_name and entity_evidence disagree')
        try:
            stamp = datetime.fromisoformat(row['reviewed_at_utc'])
            if stamp.utcoffset() is None or stamp.utcoffset().total_seconds() != 0:
                fail('reviewed_at_utc must have a UTC timezone')
        except ValueError:
            fail('invalid reviewed_at_utc')
    return rows


def write_json(path, value):
    """Replace the current run manifest atomically after each observation."""
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def collect(input_path, output_dir, delay=1.0, requester=fetch, sleeper=time.sleep):
    rows = load_seeds(input_path)  # Validate all rows before any request.
    digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / 'manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('input_sha256') != digest:
            raise ValueError('Input CSV changed; use a new output directory')
    else:
        if any(output_dir.iterdir()):
            raise ValueError('Nonempty output directory has no manifest; choose a new directory')
        manifest = {'schema_version': 1, 'input_sha256': digest, 'started_at_utc': datetime.now(timezone.utc).isoformat(), 'records': []}
        write_json(manifest_path, manifest)
    (output_dir / 'input.csv').write_bytes(input_path.read_bytes())
    records = []
    combined = []
    failed = False
    for row in rows:
        snapshot = None
        address = row['address']
        destination = output_dir / (address + '.json')
        if destination.exists():
            snapshot = json.loads(destination.read_text(encoding='utf-8'))
            if snapshot.get('address') != address or snapshot.get('source') != 'WalletExplorer':
                raise ValueError(f'Invalid cached snapshot: {destination.name}')
            normalized = normalize(snapshot['raw_response'])
            if any(snapshot.get(key) != value for key, value in normalized.items()):
                raise ValueError(f'Inconsistent cached snapshot: {destination.name}')
            record = {'address': address, 'status': normalized['lookup_status'], 'cached': True, 'snapshot': destination.name}
        else:
            try:
                url, raw = requester(address)
                normalized = normalize(raw)
            except (URLError, TimeoutError, ValueError) as exc:
                record = {'address': address, 'status': 'error', 'cached': False, 'error': str(exc)}
                failed = True
            else:
                snapshot = {'schema_version': 1, 'address': address, 'source': 'WalletExplorer',
                            'source_url': url, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
                            **normalized, 'raw_response': raw}
                with destination.open('x', encoding='utf-8') as handle:
                    json.dump(snapshot, handle, indent=2)
                    handle.write('\n')
                record = {'address': address, 'status': normalized['lookup_status'], 'cached': False, 'snapshot': destination.name}
            sleeper(delay)
        records.append(record)
        combined_row = {**row, 'lookup_status': record['status'],
                        'cached': record['cached'], 'error': record.get('error', '')}
        for field in ['wallet_id', 'service_label', 'updated_to_block', 'retrieved_at_utc', 'source_url']:
            value = snapshot.get(field) if snapshot else None
            combined_row[field] = value if value is not None else ''
        combined.append(combined_row)
        write_results(output_dir / 'results.csv', combined)
        manifest['records'] = records
        manifest['updated_at_utc'] = datetime.now(timezone.utc).isoformat()
        write_json(manifest_path, manifest)
    manifest['counts'] = {status: sum(r['status'] == status for r in records) for status in ('found', 'not_found', 'error')}
    write_json(manifest_path, manifest)
    return manifest, failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--delay', type=float, default=1.0, help='Seconds after each new lookup (minimum 1)')
    parser.add_argument('--validate-only', action='store_true', help='Check the entire input without network access')
    args = parser.parse_args()
    if not math.isfinite(args.delay) or args.delay < 1:
        parser.error('--delay must be finite and at least 1 second')
    try:
        if args.validate_only:
            print(f'Valid input: {len(load_seeds(args.input))} address(es)')
            return
        manifest, failed = collect(args.input, args.output_dir, args.delay)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'Collection failed: {exc}\n')
    print(json.dumps(manifest['counts'], indent=2))
    if failed:
        parser.exit(1, 'Some lookups failed; rerun with the same input/output to retry them.\n')


if __name__ == '__main__':
    main()
