"""Failure-oriented overlap, transitive quarantine and eligibility checks."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import audit_cryptobilis_overlap as audit


def vector(**changes):
    value = {name: 0 for name in audit.frozen.FEATURE_NAMES}
    value['median_spending_tx_fee_rate_sat_vb'] = None
    value.update(changes)
    return value


def node(key, dataset='cryptobilis', features=None, membership=0, address=None, reference=None):
    return dict(key=key, source_id=key, dataset=dataset, membership=membership,
        address_sha256=address or audit.sha(('address:' + key).encode()),
        reference_sha256=reference or audit.sha(('reference:' + key).encode()),
        features=features, cutoff_height=100, full_history_status='not_collected_for_this_source')


class OverlapTests(unittest.TestCase):
    def groups(self, nodes, prefixes=None):
        prefixes = prefixes or {n['key']: [] for n in nodes}
        links = audit.link_catalog(nodes, prefixes)
        a = audit.components([n['key'] for n in nodes], links)
        b = audit.independent_components([n['key'] for n in nodes], links)
        self.assertEqual(a, b)
        return links, a

    def test_exact_address_joins_even_unavailable_sources(self):
        nodes = [node('d', 'coldcard', address='a'), node('e', address='a')]
        _, groups = self.groups(nodes)
        self.assertEqual(groups, [['d', 'e']])

    def test_common_reference_joins_without_available_features(self):
        _, groups = self.groups([node('d', 'coldcard', reference='r'), node('e', reference='r')])
        self.assertEqual(groups, [['d', 'e']])

    def test_common_prior_transaction_joins(self):
        nodes = [node('d', 'coldcard'), node('e')]
        _, groups = self.groups(nodes, {key: [dict(transaction_id='same')] for key in ('d', 'e')})
        self.assertEqual(groups, [['d', 'e']])

    def test_cross_role_transaction_joins(self):
        nodes = [node('d', 'coldcard', reference='shared'), node('e')]
        links, groups = self.groups(nodes, {'d': [], 'e': [dict(transaction_id='shared')]})
        self.assertEqual(groups, [['d', 'e']])
        self.assertEqual(links['transaction_any_role']['shared'], {'d', 'e'})
        self.assertEqual(links['prior_transaction']['shared'], {'e'})

    def test_identical_vectors_join_across_datasets(self):
        _, groups = self.groups([node('d', 'coldcard', vector()), node('e', features=vector())])
        self.assertEqual(groups, [['d', 'e']])

    def test_unavailable_vectors_never_all_join_as_null(self):
        _, groups = self.groups([node('d', 'coldcard'), node('e')])
        self.assertEqual(groups, [['d'], ['e']])

    def test_exact_numeric_equality_int_float(self):
        self.assertEqual(audit.frozen.vector_key(vector(balance_sat=1)),
                         audit.frozen.vector_key(vector(balance_sat=1.0)))

    def test_large_distinct_integers_do_not_collapse(self):
        self.assertNotEqual(audit.frozen.vector_key(vector(balance_sat=2**60)),
                            audit.frozen.vector_key(vector(balance_sat=2**60 + 1)))

    def test_missingness_is_part_of_vector_identity(self):
        self.assertNotEqual(audit.frozen.vector_key(vector()),
                            audit.frozen.vector_key(vector(median_spending_tx_fee_rate_sat_vb=0)))

    def test_transitive_quarantine_includes_non_direct_external_member(self):
        d = node('d', 'coldcard', vector(balance_sat=11), reference='shared')
        a = node('a', features=vector(balance_sat=22), reference='shared')
        b = node('b', features=vector(balance_sat=22))
        _, groups = self.groups([d, a, b])
        records, assignments = audit.classify([d, a, b], groups)
        self.assertEqual(len(records), 1)
        self.assertEqual({x['status'] for x in assignments}, {'quarantined_cross_development_component'})

    def test_unavailable_bridge_retains_null_and_quarantines_complete_neighbor(self):
        nodes = [node('d', 'coldcard', vector(), address='x'),
                 node('a', address='x', reference='r'), node('b', features=vector(balance_sat=9), reference='r')]
        _, groups = self.groups(nodes)
        _, assignments = audit.classify(nodes, groups)
        self.assertEqual({x['source_id']: x['status'] for x in assignments},
                         {'a': 'excluded_bounded_incomplete', 'b': 'quarantined_cross_development_component'})

    def test_unlinked_complete_source_is_eligible(self):
        n = node('e', features=vector())
        _, assignments = audit.classify([n], [['e']])
        self.assertEqual(assignments[0]['status'], 'eligible_for_frozen_proxy_evaluation')

    def test_component_coverage_and_duplicates_rejected(self):
        n = node('e')
        for nodes, groups in [([n], []), ([n], [['e', 'e']]), ([n, n], [['e']])]:
            with self.subTest(groups=groups), self.assertRaises(ValueError):
                audit.classify(nodes, groups)


class EvidenceTests(unittest.TestCase):
    def fixture(self):
        prefix = [dict(transaction_id='a' * 64, height=10,
                       received=[dict(outpoint_id='b' * 64, value_sat=20)], spent=[],
                       spending_tx_fee_sat=None, spending_tx_vsize_vb=None)]
        features = audit.frozen.features(prefix, 100)
        row = dict(source_id='s', address_sha256='c' * 64, cutoff_height=100,
                   payment_txid_sha256='d' * 64, features=features,
                   precutoff_history_status='complete_full_history')
        entry = dict(source_id='s', address_sha256='c' * 64, cutoff_height=100,
                     features=features, status='complete', prefix=prefix)
        return row, entry

    def test_good_normalized_vector_reproduces(self):
        row, entry = self.fixture()
        self.assertEqual(audit.normalized_prefix(row, entry), entry['prefix'])

    def test_changed_vector_rejected(self):
        row, entry = self.fixture();row['features'] = vector()
        with self.assertRaisesRegex(ValueError, 'vector mismatch'):
            audit.normalized_prefix(row, entry)

    def test_future_or_reference_block_transaction_rejected(self):
        for height in (100, 101):
            row, entry = self.fixture();entry['prefix'][0]['height'] = height
            with self.subTest(height=height), self.assertRaisesRegex(ValueError, 'future transaction'):
                audit.normalized_prefix(row, entry)

    def test_reference_transaction_in_prefix_rejected(self):
        row, entry = self.fixture();row['payment_txid_sha256'] = 'a' * 64
        with self.assertRaisesRegex(ValueError, 'Reference transaction leaked'):
            audit.normalized_prefix(row, entry)

    def test_partial_prefix_cannot_supply_a_vector(self):
        row, entry = self.fixture();entry['status'] = 'bounded_incomplete'
        with self.assertRaisesRegex(ValueError, 'Unfinished source'):
            audit.normalized_prefix(row, entry)

    def test_bounded_prefix_must_keep_null(self):
        row, entry = self.fixture();row.update(features=None, precutoff_history_status='bounded_incomplete')
        entry.update(features=None, status='bounded_incomplete', prefix=None)
        self.assertEqual(audit.normalized_prefix(row, entry), [])
        entry['prefix'] = []
        with self.assertRaisesRegex(ValueError, 'Unfinished prefix'):
            audit.normalized_prefix(row, entry)

    def test_mismatched_identity_rejected(self):
        row, entry = self.fixture();entry['source_id'] = 'other'
        with self.assertRaisesRegex(ValueError, 'source ID mismatch'):
            audit.normalized_prefix(row, entry)

    def test_tampered_or_traversing_pin_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);p = root / 'data.json';p.write_text('{}')
            pin = dict(file='data.json', sha256=audit.sha(p.read_bytes()))
            self.assertEqual(audit.resolve_pin(root, pin), p)
            p.write_text('[]')
            with self.assertRaisesRegex(ValueError, 'fingerprint mismatch'):
                audit.resolve_pin(root, pin)
            with self.assertRaisesRegex(ValueError, 'outside research root'):
                audit.resolve_pin(root, dict(file='../outside', sha256='0' * 64))


if __name__ == '__main__':
    unittest.main()
