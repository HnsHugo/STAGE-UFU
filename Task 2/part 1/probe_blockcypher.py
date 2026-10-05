"""Read-only test of provider height filtering; not a production collector."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import urlopen

ADDRESS = '1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g'
BASE = 'https://api.blockcypher.com/v1/btc/main/addrs/'


def validate(data, address, before, after=None):
    if data.get('address') != address:
        raise ValueError('Address mismatch')
    refs = data.get('txrefs', [])
    violations = [r['block_height'] for r in refs
                  if r['block_height'] >= before or (after is not None and r['block_height'] <= after)]
    return {'references': len(refs), 'has_more': data.get('hasMore'),
            'min_height': min((r['block_height'] for r in refs), default=None),
            'max_height': max((r['block_height'] for r in refs), default=None),
            'out_of_bounds_references': len(violations),
            'filter_observation': 'violated' if violations else ('no_counterexample' if refs else 'empty_inconclusive')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    cases = [('before_only', {'before': 960100, 'limit': 10, 'confirmations': 1}),
             ('height_interval', {'before': 960100, 'after': 960000, 'limit': 10, 'confirmations': 1})]
    report = []
    for name, params in cases:
        url = BASE + ADDRESS + '?' + urlencode(params)
        record = {'case': name, 'url': url,
                  'retrieved_at_utc': datetime.now(timezone.utc).isoformat()}
        try:
            with urlopen(url, timeout=30) as response:
                raw = response.read()
                record['http_status'] = response.status
            data = json.loads(raw)
            (args.output_dir / (name + '.raw.json')).write_bytes(raw)
            record['response_sha256'] = hashlib.sha256(raw).hexdigest()
            record.update(validate(data, ADDRESS, params['before'], params.get('after')))
        except Exception as exc:
            record['error'] = str(exc)
        report.append(record)
        time.sleep(1)
    (args.output_dir / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
