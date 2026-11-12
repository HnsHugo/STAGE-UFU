import asyncio
import copy
import gzip
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

import independent_mempool_pilot as pilot
from build_source_registry import json_bytes


def fixture(work):
    record = dict(pilot_id='test_source', address='synthetic-address', payment_txid='reference',
        cutoff_height=10, cutoff_block_hash='block-10', registry_input_slots=1, reference_input_value_sat=10)
    parent = dict(txid='parent', version=2, locktime=0, size=100, weight=400, fee=0,
        vin=[dict(is_coinbase=True)], vout=[dict(scriptpubkey='synthetic-script',
            scriptpubkey_address=record['address'], value=10)],
        status=dict(confirmed=True, block_height=1, block_hash='block-1', block_time=100))
    anchor = dict(txid='reference', vin=[dict(txid='parent', vout=0,
        prevout=dict(scriptpubkey_address=record['address'], value=10))],
        status=dict(confirmed=True, block_height=10, block_hash='block-10'))
    folder = work / 'legacy' / record['pilot_id']; folder.mkdir(parents=True)
    pins = {}
    for key, value, endpoint in [('reference', anchor, '/tx/reference'),
        ('tail_0000', [parent], '/address/synthetic-address/txs/chain/reference'),
        ('tail_0001', [], '/address/synthetic-address/txs/chain/parent')]:
        body = folder / (key + '.json.gz'); body.write_bytes(gzip.compress(json_bytes(value), mtime=0))
        pin = dict(source_id=record['pilot_id'], key=key, sha256=pilot.sha(body),
            endpoint_sha256=hashlib.sha256(endpoint.encode()).hexdigest())
        pilot.write(folder / (key + '.json'), dict(pin, http_status=200))
        pins[key] = pin
    return record, pins, parent


class IndependentProviderContracts(unittest.TestCase):
    def test_frozen_reference_anchor_rejects_other_chain_height_and_unconfirmed(self):
        record = dict(cutoff_height=10, cutoff_block_hash='block-10')
        status = dict(confirmed=True, block_height=10, block_hash='block-10')
        pilot.status_check(record, status)
        for update in [dict(confirmed=False), dict(block_height=11), dict(block_hash='other')]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                pilot.status_check(record, dict(status, **update))

    def test_boundary_comparison_keeps_predictor_and_outpoint_fields(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, parent = fixture(Path(td))
            extra = dict(parent, presentation_only='unused')
            self.assertEqual(pilot.core(parent), pilot.core(extra))
            for field in ['fee', 'weight', 'size']:
                changed = copy.deepcopy(parent); changed[field] += 1
                self.assertNotEqual(pilot.core(parent), pilot.core(changed))
            changed = copy.deepcopy(parent); changed['vout'][0]['value'] += 1
            self.assertNotEqual(pilot.core(parent), pilot.core(changed))

    def test_saved_empty_page_is_retained_and_cached_funding_closes(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td); record, pins, _ = fixture(work)
            anchor, pages, transactions, cursor = pilot.legacy_source(record, work, pins)
            self.assertEqual(pages[-1], [])
            self.assertEqual(cursor, 'parent')
            result = pilot.tail.tail_check(record, anchor, transactions, True, anchor['status'], {})
            self.assertEqual(result['status'], 'complete_prior_prefix')
            self.assertEqual(len(result['features']), 14)

    def test_changed_cache_body_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td); record, pins, _ = fixture(work)
            (work / 'legacy/test_source/tail_0000.json.gz').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'fingerprint'):
                pilot.legacy_source(record, work, pins)

    def test_budget_and_consumed_marker_issue_no_extra_http(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td); http = Mock(); http.get_json.return_value = {}
            http.last_dispatch_at = '2026-11-12T00:00:00+00:00'
            requests = pilot.Requests(work, http, 1)
            record = dict(pilot_id='test_source')
            requests.get(record, 'first', '/tx/synthetic/status')
            requests.maximum = 2
            with self.assertRaisesRegex(ValueError, 'Consumed'):
                requests.get(record, 'first', '/tx/synthetic/status')
            requests.maximum = 1
            with self.assertRaises(ValueError):
                requests.get(record, 'again', '/tx/synthetic/status')
            self.assertEqual(http.get_json.call_count, 1)

    def test_blockstream_url_is_not_accessible_through_new_transport(self):
        http = pilot.MempoolHTTP(.2)
        with self.assertRaisesRegex(ValueError, 'provider'):
            asyncio.run(http.request('https://blockstream.info/api/tx/synthetic/status', 15))

    def test_independent_terminal_disagreement_cannot_promote_a_vector(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td); record, pins, parent = fixture(work)
            requests = Mock(); requests.get.side_effect = [dict(confirmed=True, block_height=10,
                block_hash='block-10'), parent, [dict(parent, txid='unexpected')]]
            with self.assertRaisesRegex(ValueError, 'terminal'):
                pilot.collect(record, requests, work, dict(max_pages_per_address=32), pins)
            self.assertEqual(requests.get.call_count, 3)
            self.assertFalse((work / 'results').exists())


if __name__ == '__main__':
    unittest.main()
