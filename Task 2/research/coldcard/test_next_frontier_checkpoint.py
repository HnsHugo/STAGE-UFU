"""Contracts for the next fixed selection and inherited collection gates."""
import copy
import hashlib
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from prepare_next_frontier_checkpoint import choose_next, inherited_inputs


class NextFrontierContracts(unittest.TestCase):
    def fixture(self):
        ids = [f'comparison_{i:04d}' for i in range(351, 376)]
        records = []
        rows = []
        for sid in ids:
            r = dict(pilot_id=sid, address='address-' + sid, payment_txid='payment-' + sid,
                cutoff_height=10, cutoff_block_hash='frozen-block')
            r['address_sha256'] = hashlib.sha256(r['address'].encode()).hexdigest()
            r['payment_txid_sha256'] = hashlib.sha256(r['payment_txid'].encode()).hexdigest()
            records.append(r)
            rows.append(dict(source_id=sid, features=None, **{k: r[k] for k in
                ['address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash']}))
        resume = dict(coldcard_unextended_at_16_page_bound_source_ids=ids,
            next_extension_source_ids=ids[:20], source_ids=['comparison_0241'])
        return resume, dict(rows=rows), records

    def test_twenty_in_frozen_order_and_no_complete_or_preceding_source(self):
        resume, view, records = self.fixture()
        self.assertEqual(choose_next(resume, view, records)[0], resume['next_extension_source_ids'])
        changed = copy.deepcopy(view)
        changed['rows'][0]['features'] = {'existing': 1}
        with self.assertRaises(AssertionError):
            choose_next(resume, changed, records)
        with self.assertRaises(AssertionError):
            choose_next(dict(resume, source_ids=[records[0]['pilot_id']]), view, records)
        with self.assertRaises(AssertionError):
            choose_next(dict(resume, next_extension_source_ids=resume['next_extension_source_ids'][::-1]), view, records)

    def test_private_identity_mutation_and_duplicate_registry_are_rejected(self):
        resume, view, records = self.fixture()
        for field in ['address', 'payment_txid', 'cutoff_height', 'cutoff_block_hash']:
            changed = copy.deepcopy(records)
            changed[0][field] = 'changed'
            with self.subTest(field=field), self.assertRaises(AssertionError):
                choose_next(resume, view, changed)
        with self.assertRaises(AssertionError):
            choose_next(resume, view, records + records[:1])

    def test_ancestor_file_hash_pairs_and_exact_pilot_alias_survive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent, output = root / 'parent', root / 'next'
            parent.mkdir(); output.mkdir()
            payload = parent / 'gate.json'; payload.write_bytes(b'validated-gate')
            pin = dict(file='gate.json', sha256=hashlib.sha256(payload.read_bytes()).hexdigest())
            result = inherited_inputs(dict(inputs=dict(pilot_validation=pin, old_gate=pin)), parent, output)
            self.assertEqual(result['pilot_validation'], result['prior_pilot_validation'])
            self.assertTrue(all((output / p['file']).resolve() == payload for p in result.values()))
            payload.write_bytes(b'changed-gate')
            with self.assertRaises(AssertionError):
                inherited_inputs(dict(inputs=dict(pilot_validation=pin)), parent, output)

    def test_real_next_protocol_uses_original_eight_control_gate_without_http(self):
        import collect_reference_tail_many as many
        root = Path(__file__).resolve().parent
        scope = root / 'source_prefix_extension_20261112_03'
        with patch.object(many.tail, 'run') as runner, patch.object(many, 'verify', return_value=0):
            many.main(scope / 'protocol.json', scope, root / ('source_cohort_work_' + scope.name))
            runner.assert_called_once()


if __name__ == '__main__':
    unittest.main()
