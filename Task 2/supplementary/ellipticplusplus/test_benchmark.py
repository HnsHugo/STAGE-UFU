import unittest
import numpy as np
import pandas as pd
from train_benchmark import prepare, split_indices, evaluate


class BenchmarkTests(unittest.TestCase):
    def test_repeated_profiles_collapse_and_unknowns_are_excluded(self):
        features = pd.DataFrame({'address': ['a', 'a', 'b'], 'Time step': [1, 2, 1], 'amount': [5, 5, 8]})
        labels = pd.DataFrame({'address': ['a', 'b'], 'class': [1, 3]})
        result = prepare(features, labels)
        self.assertEqual(result.address.tolist(), ['a'])
        self.assertNotIn('Time step', result)

    def test_inconsistent_profiles_are_rejected(self):
        features = pd.DataFrame({'address': ['a', 'a'], 'Time step': [1, 2], 'amount': [5, 6]})
        labels = pd.DataFrame({'address': ['a'], 'class': [1]})
        with self.assertRaises(ValueError):
            prepare(features, labels)

    def test_missing_coverage_and_duplicate_labels_are_rejected(self):
        features = pd.DataFrame({'address': ['a'], 'Time step': [1], 'amount': [5]})
        for labels in [pd.DataFrame({'address': ['b'], 'class': [1]}),
                       pd.DataFrame({'address': ['a', 'a'], 'class': [1, 2]})]:
            with self.assertRaises(ValueError):
                prepare(features, labels)

    def test_splits_are_disjoint_exhaustive_and_reproducible(self):
        data = pd.DataFrame({'address': [str(i) for i in range(100)], 'class': [1]*20 + [2]*80})
        parts = split_indices(data)
        self.assertEqual([len(p) for p in parts], [60, 20, 20])
        self.assertEqual(len(set(np.concatenate(parts))), 100)
        for actual, repeated in zip(parts, split_indices(data)):
            np.testing.assert_array_equal(actual, repeated)
        self.assertEqual([int((data.iloc[p]['class'] == 1).sum()) for p in parts], [12, 4, 4])

    def test_metrics_count_both_types_of_errors(self):
        result = evaluate([1, 1, 0, 0], [1, 0, 1, 0], [0.9, 0.1, 0.8, 0.2])
        self.assertEqual(result['false_positive'], 1)
        self.assertEqual(result['false_negative'], 1)
        self.assertEqual(result['precision'], .5)
        self.assertEqual(result['recall'], .5)


if __name__ == '__main__':
    unittest.main()
