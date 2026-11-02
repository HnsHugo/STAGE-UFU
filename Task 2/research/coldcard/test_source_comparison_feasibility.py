"""Failure-oriented checks for the offline grouping and cutoff audit."""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest

import audit_source_comparison_feasibility as audit


def h(value):
    return hashlib.sha256(value.encode()).hexdigest()


def row(key, label=0, number=1):
    return dict(source_id=key, address_sha256=h('address:' + key),
                payment_txid_sha256=h('payment:' + key), cutoff_height=100,
                cutoff_block_hash=h('block'), known_coldcard_core_membership=label,
                features={k: number for k in audit.FEATURE_NAMES})


class GroupingTests(unittest.TestCase):
    def test_transitive_components_across_distinct_link_criteria(self):
        rows = [row(str(i), number=i) for i in range(5)]
        rows[1]['address_sha256'] = rows[0]['address_sha256']
        rows[2]['payment_txid_sha256'] = rows[1]['payment_txid_sha256']
        rows[4]['features'] = deepcopy(rows[3]['features'])
        prefixes = {str(i): [] for i in range(5)}
        prefixes['2'] = prefixes['3'] = [dict(transaction_id=h('shared'))]
        links = audit.link_sets(rows, prefixes)
        groups = audit.components(rows, links)
        self.assertEqual(groups, [['0', '1', '2', '3', '4']])
        audit.check_components_independently(rows, links, groups)
        with self.assertRaisesRegex(ValueError, 'traversal disagrees'):
            audit.check_components_independently(rows, links, [['0', '1', '2'], ['3', '4']])

    def test_full_vectors_include_missingness_and_preserve_numeric_precision(self):
        a = row('a')['features']
        b = {k: 1.0 for k in a}
        self.assertEqual(audit.vector_key(a), audit.vector_key(b))
        b[audit.FEATURE_NAMES[0]] = None
        self.assertNotEqual(audit.vector_key(a), audit.vector_key(b))
        a[audit.FEATURE_NAMES[0]] = 2**60
        b = deepcopy(a)
        b[audit.FEATURE_NAMES[0]] += 1
        self.assertNotEqual(audit.vector_key(a), audit.vector_key(b))
        b[audit.FEATURE_NAMES[0]] = True
        with self.assertRaisesRegex(ValueError, 'Invalid feature'):
            audit.vector_key(b)

    def test_nonfinite_features_are_rejected(self):
        for bad in (float('nan'), float('inf'), -float('inf')):
            vector = row('bad')['features']
            vector[audit.FEATURE_NAMES[0]] = bad
            with self.assertRaises(ValueError):
                audit.vector_key(vector)

    def test_frozen_hash_and_unrescued_insufficient_partitions(self):
        rows = [row('a', 1), row('b')]
        groups = [['a'], ['b']]
        links = audit.link_sets(rows, {'a': [], 'b': []})
        result = audit.evaluate_partitions(rows, groups, links)
        self.assertFalse(result['feasible'])
        self.assertGreater(len(result['failures']), 0)
        expected = int.from_bytes(hashlib.sha256(('coldcard-source-split-v1:42:' + rows[0]['address_sha256']).encode()).digest(), 'big') % 10
        self.assertEqual(audit.partition_for(rows[0]['address_sha256']),
                         'train' if expected < 7 else 'validation' if expected == 7 else 'test')
        self.assertEqual(audit.evaluate_partitions(rows, groups, links), result)
        self.assertEqual(groups, [['a'], ['b']])

    def test_crossing_shared_evidence_fails_even_with_enough_rows(self):
        rows = [row(str(i), i % 2, i) for i in range(1200)]
        prefixes = {r['source_id']: [] for r in rows}
        links = audit.link_sets(rows, prefixes)
        by_bucket = {}
        for r in rows:
            by_bucket.setdefault(audit.partition_for(r['address_sha256']), r['source_id'])
        self.assertEqual(set(by_bucket), {'train', 'validation', 'test'})
        links['prior_transaction'][h('crossing')] = {by_bucket['train'], by_bucket['test']}
        result = audit.evaluate_partitions(rows, [[r['source_id']] for r in rows], links)
        self.assertTrue(all(c[k] >= 20 for c in result['counts'].values() for k in ('case', 'comparison')))
        self.assertFalse(result['feasible'])
        self.assertEqual(result['cross_partition_link_groups']['prior_transaction'], 1)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.row = row('a', 1)
        self.prefix = [dict(transaction_id=h('funding'), height=99,
                            received=[dict(outpoint_id=h('funding:0'), value_sat=100)],
                            spent=[], spending_tx_fee_sat=None, spending_tx_vsize_vb=None)]
        self.row['features'] = audit.features(self.prefix, 100)
        self.entry = dict(status='complete', prefix=self.prefix, features=self.row['features'],
                          address_sha256=self.row['address_sha256'], cutoff_height=100)

    def test_strict_cutoff_and_reference_exclusion(self):
        audit.check_prefix(self.row, self.entry)
        self.prefix[0]['height'] = 100
        with self.assertRaisesRegex(ValueError, 'Non-prior-block'):
            audit.check_prefix(self.row, self.entry)
        self.prefix[0]['height'] = 99
        self.prefix[0]['transaction_id'] = self.row['payment_txid_sha256']
        with self.assertRaisesRegex(ValueError, 'Reference payment'):
            audit.check_prefix(self.row, self.entry)

    def test_unfinished_evidence_cannot_supply_vector(self):
        self.entry['status'] = 'bounded_incomplete'
        with self.assertRaisesRegex(ValueError, 'Unfinished'):
            audit.check_prefix(self.row, self.entry)

    def test_join_and_vector_tampering_fail(self):
        self.entry['address_sha256'] = h('other')
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            audit.check_prefix(self.row, self.entry)
        self.entry['address_sha256'] = self.row['address_sha256']
        self.entry['features'] = deepcopy(self.row['features'])
        self.entry['features']['balance_sat'] += 1
        with self.assertRaisesRegex(ValueError, 'reproduction mismatch'):
            audit.check_prefix(self.row, self.entry)

    def test_duplicate_transaction_and_unclosed_funding_fail(self):
        self.prefix.append(deepcopy(self.prefix[0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate prefix transaction'):
            audit.check_prefix(self.row, self.entry)
        self.prefix.pop()
        self.prefix[0]['spent'] = [dict(outpoint_id=h('unobserved'), value_sat=100)]
        self.prefix[0]['spending_tx_fee_sat'] = 1
        self.prefix[0]['spending_tx_vsize_vb'] = 100
        with self.assertRaisesRegex(ValueError, 'spent output absent'):
            audit.check_prefix(self.row, self.entry)

    def test_modified_input_pin_and_path_escape_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'evidence.json'
            path.write_bytes(b'{}')
            pin = dict(file=path.name, sha256=audit.digest(b'{}'))
            self.assertEqual(audit.read_pin(root, pin), path)
            path.write_bytes(b'{"changed":true}')
            with self.assertRaisesRegex(ValueError, 'fingerprint mismatch'):
                audit.read_pin(root, pin)
            pin['file'] = '../outside.json'
            with self.assertRaisesRegex(ValueError, 'outside audit root'):
                audit.read_pin(root, pin)

    def test_coverage_retains_unavailable_selected_rows(self):
        other = row('b')
        other['features'] = None
        counts = audit.coverage([self.row, other])
        self.assertEqual(counts[0]['coverage_fraction'], 1)
        self.assertEqual(counts[1]['selected'], 1)
        self.assertEqual(counts[1]['coverage_fraction'], 0)
        self.assertIsNone(other['features'])


if __name__ == '__main__':
    unittest.main()
