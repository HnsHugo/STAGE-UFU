"""Regression checks for supplemental cursor coverage and request consumption."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest.mock import Mock
import urllib.error

from build_source_registry import digest, json_bytes
from collect_comparison_coverage import Pages, finish_source
from test_source_cohort import history, records


class CoverageTests(unittest.TestCase):
    def fixture(self):
        record = records(1)[0]
        record.update(payment_txid_sha256=digest(record['payment_txid'].encode()),
                      registry_input_slots=1, reference_input_value_sat=60)
        return record, history(record)

    def test_400_transactions_require_terminal_seventeenth_page_and_resume_without_http(self):
        record, data = self.fixture()
        # Append 396 later receipts; the existing strictly prior vector stays fixed.
        for index in range(396):
            tx = deepcopy(data['transactions'][0])
            tx.update(txid='later_%04d' % index, vin=[])
            tx['status']['block_height'] = 40
            data['transactions'].append(tx)
        txs = sorted(data['transactions'], key=lambda tx:-tx['status']['block_height'])
        stats = data['before']['chain_stats']
        extra = data['transactions'][4:]
        stats['tx_count'] = 400
        stats['funded_txo_count'] += sum(sum(o.get('scriptpubkey_address') == record['address'] for o in tx['vout']) for tx in extra)
        stats['funded_txo_sum'] += sum(sum(o['value'] for o in tx['vout'] if o.get('scriptpubkey_address') == record['address']) for tx in extra)
        counter = dict(address=record['address'], chain_stats=stats)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            chunks = iter([txs[i:i+25] for i in range(0,400,25)] + [[]])
            http = Mock()
            http.get_json.side_effect = lambda url, timeout: next(chunks) if '/txs/chain' in url else counter
            pages = Pages(root, http, Event())
            pages.get(record, 'before', '/address/' + record['address'])
            result = finish_source(record, pages, root)
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['features']['balance_sat'], 60)
            self.assertTrue(all(t['height'] < 20 for t in result['prefix']))
            self.assertEqual(http.get_json.call_count, 19)
            self.assertEqual(finish_source(record, pages, root), result)
            self.assertEqual(http.get_json.call_count, 19)

    def test_429_stops_and_consumes_request_without_retry(self):
        record, _ = self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            http = Mock()
            http.get_json.side_effect = urllib.error.HTTPError('url', 429, 'rate limit', {'Retry-After':'90000'}, None)
            stop = Event()
            pages = Pages(Path(folder), http, stop)
            with self.assertRaises(urllib.error.HTTPError):
                pages.get(record, 'before', '/address/source')
            self.assertTrue(stop.is_set())
            with self.assertRaises(RuntimeError):
                pages.get(record, 'before', '/address/source')
            self.assertEqual(http.get_json.call_count, 1)
            marker = json.loads((Path(folder)/'requests'/record['pilot_id']/'before.json').read_bytes())
            self.assertEqual(marker['retry_after'], '90000')

    def test_saved_page_is_verified_before_offline_reuse(self):
        record, _ = self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            http = Mock()
            http.get_json.return_value = []
            pages = Pages(Path(folder), http, Event())
            pages.get(record, 'page_000000', '/address/source/txs/chain')
            body = Path(folder)/'requests'/record['pilot_id']/'page_000000.json.gz'
            body.write_bytes(gzip.compress(json_bytes([{}]), mtime=0))
            with self.assertRaises(ValueError):
                pages.get(record, 'page_000000', '/address/source/txs/chain')
            self.assertEqual(http.get_json.call_count, 1)


if __name__ == '__main__':
    unittest.main()
