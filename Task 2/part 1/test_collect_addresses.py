import csv
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import URLError
from collect_addresses import FIELDS, collect, load_seeds

ADDRESS = '16SbwNa22nBwhLtg6HzWVYFQiUxtNzAUpt'


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / 'seeds.csv'
        self.row = dict.fromkeys(FIELDS, '')
        self.row.update(address=ADDRESS, network='bitcoin_mainnet', purpose='api_smoke_test',
                        entity_name='unknown', entity_evidence='unknown', storage_type='unknown',
                        hardware_wallet='unknown', illicit_label='unknown', reviewed_at_utc='2026-10-05T00:00:00+00:00')
        self.write([self.row])

    def write(self, rows):
        with self.input.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def test_duplicate_and_unsourced_claim_rejected_before_network(self):
        for rows in ([self.row, self.row], [{**self.row, 'storage_type': 'cold'}]):
            self.write(rows)
            with self.assertRaises(ValueError):
                collect(self.input, self.root / 'out', requester=lambda _: self.fail('Network called'))

    def test_failure_is_retried_and_success_cached(self):
        out = self.root / 'out'
        def fail(_):
            raise URLError('offline')
        manifest, failed = collect(self.input, out, requester=fail, sleeper=lambda _: None)
        self.assertTrue(failed)
        self.assertEqual(manifest['counts']['error'], 1)
        self.assertFalse((out / (ADDRESS + '.json')).exists())
        manifest, failed = collect(self.input, out, requester=lambda _: ('https://example.test', {'found': True, 'wallet_id': 'abc'}), sleeper=lambda _: None)
        self.assertFalse(failed)
        saved = (out / (ADDRESS + '.json')).read_bytes()
        manifest, _ = collect(self.input, out, requester=lambda _: self.fail('Cached request repeated'))
        self.assertTrue(manifest['records'][0]['cached'])
        self.assertEqual(saved, (out / (ADDRESS + '.json')).read_bytes())

    def test_not_found_is_distinct_and_cached(self):
        manifest, failed = collect(self.input, self.root / 'out', requester=lambda _: ('https://example.test', {'found': False}), sleeper=lambda _: None)
        self.assertFalse(failed)
        self.assertEqual(manifest['counts'], {'found': 0, 'not_found': 1, 'error': 0})

    def test_changed_input_and_broken_cache_rejected(self):
        out = self.root / 'out'
        collect(self.input, out, requester=lambda _: ('https://example.test', {'found': False}), sleeper=lambda _: None)
        path = out / (ADDRESS + '.json')
        snapshot = json.loads(path.read_text())
        snapshot['lookup_status'] = 'found'
        path.write_text(json.dumps(snapshot))
        with self.assertRaises(ValueError):
            collect(self.input, out)
        self.row['notes'] = 'Changed'
        self.write([self.row])
        with self.assertRaisesRegex(ValueError, 'changed'):
            collect(self.input, out)


if __name__ == '__main__':
    unittest.main()
