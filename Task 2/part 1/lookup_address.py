"""Capture an address-to-cluster observation from WalletExplorer (Python 3.10+)."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = 'https://www.walletexplorer.com/api/1/address-lookup'


def normalize(payload):
    """Keep a negative lookup distinct from errors and an unnamed cluster."""
    if not isinstance(payload, dict):
        raise ValueError('Expected a JSON object')
    if 'error' in payload:
        raise ValueError(f"WalletExplorer error: {payload['error']}")
    if type(payload.get('found')) is not bool:
        raise ValueError('Missing or invalid found flag')
    if payload['found']:
        if not isinstance(payload.get('wallet_id'), str) or not payload['wallet_id']:
            raise ValueError('Found response has no wallet_id')
    return {
        'lookup_status': 'found' if payload['found'] else 'not_found',
        'wallet_id': payload.get('wallet_id') if payload['found'] else None,
        'service_label': payload.get('label') if payload['found'] else None,
        'updated_to_block': payload.get('updated_to_block'),
    }


def fetch(address):
    url = BASE_URL + '?' + urlencode({'address': address})
    request = Request(url, headers={'User-Agent': 'UFU-academic-wallet-analysis/0.1'})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            return url, payload
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** (attempt + 1))
    raise RuntimeError('Request failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('address', help='Public Bitcoin mainnet address; never a seed or private key')
    parser.add_argument('--output', type=Path, required=True, help='New snapshot JSON path')
    args = parser.parse_args()
    # Reject accidental whitespace and unbounded input; this is not checksum validation.
    if not 14 <= len(args.address) <= 90 or not args.address.isalnum():
        parser.error('Expected an alphanumeric public address (14–90 characters)')
    if args.output.exists():
        parser.error('Output exists; choose a new path to preserve the earlier observation')
    try:
        url, raw = fetch(args.address)
        result = normalize(raw)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        parser.exit(1, f'Lookup failed; no observation saved: {exc}\n')
    snapshot = {
        'schema_version': 1,
        'address': args.address,
        'source': 'WalletExplorer',
        'source_url': url,
        'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
        **result,
        'raw_response': raw,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(snapshot, handle, indent=2, ensure_ascii=False)
        handle.write('\n')
    print(json.dumps(result, indent=2))
    print(f'Snapshot: {args.output}')


if __name__ == '__main__':
    main()
