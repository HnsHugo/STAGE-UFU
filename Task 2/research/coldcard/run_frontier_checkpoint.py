"""Reuse the original guarded route; reject changed recovered bodies before extension."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def verify_recovered_response(expected, marker):
    for key in ['source_id', 'key', 'sha256', 'endpoint_sha256']:
        if marker.get(key) != expected[key]:
            raise ValueError('Recovered old response differs from pinned ' + key)
    if marker.get('http_status') != 200 or marker.get('offline_reused'):
        raise ValueError('Old missing body must be explicitly recovered through the guarded route')


def main(protocol_path, output, work):
    from run_after_cooldown import cooldown_due
    protocol = json.loads(protocol_path.read_bytes())
    if not cooldown_due(protocol, datetime.now(timezone.utc)):
        print('COOLDOWN_NOT_DUE_NO_HTTP', flush=True)
        return
    pin = protocol['inputs']['expected_recovery_manifest']
    path = (protocol_path.parent / pin['file']).resolve()
    if hashlib.sha256(path.read_bytes()).hexdigest() != pin['sha256']:
        raise ValueError('Recovery contract changed')
    expected = {(m['source_id'], m['key']): m for m in json.loads(path.read_bytes())['responses']}
    import collect_reference_tail as tail
    original = tail.Pages

    class RecoveryPages(original):
        def get(self, record, key, endpoint):
            try:
                data = super().get(record, key, endpoint)
                identity = (record['pilot_id'], key)
                if identity in expected:
                    marker = json.loads((work / 'requests' / record['pilot_id'] / (key + '.json')).read_bytes())
                    verify_recovered_response(expected[identity], marker)
                return data
            except Exception:
                self.stop.set()
                raise

    tail.Pages = RecoveryPages
    source = BASE / 'source_prefix_extension_20261109_01/run_scope.py'
    spec = importlib.util.spec_from_file_location('guarded_frontier_scope', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.main(protocol_path, output, work)
    finally:
        tail.Pages = original


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['protocol', 'output', 'work']:
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    main(args.protocol.resolve(), args.output.resolve(), args.work.resolve())
