import unittest
import numpy as np
from compare_grouped_baselines import fit_stump, describe, summarize, VARIANTS


class BaselineTests(unittest.TestCase):
    def test_threshold_comes_from_training_and_test_is_unseen(self):
        x = np.array([0.] * 30 + [10.] * 30)
        y = np.array([0] * 30 + [1] * 30)
        model = fit_stump(x, y)
        before = describe(model)
        np.testing.assert_array_equal(model.predict(np.array([[1.], [1000.]])), [0, 1])
        self.assertEqual(describe(model), before)
        self.assertEqual(before['threshold'], 5.)

    def test_constant_feature_is_valid_constant_baseline(self):
        model = fit_stump(np.zeros(60), np.array([0] * 30 + [1] * 30))
        self.assertIsNone(describe(model)['threshold'])
        self.assertEqual(describe(model)['node_count'], 1)

    def test_nonfinite_rejected_and_no_identifier_feature(self):
        with self.assertRaises(ValueError): fit_stump(np.array([np.nan, 1.]), [0, 1])
        self.assertEqual(set(VARIANTS.values()), {'fee_rate_sat_vb', 'output_count', 'output_total_sat'})

    def test_imbalanced_constant_prediction_has_half_balanced_accuracy(self):
        result = summarize(np.array([0] * 99 + [1]), np.zeros(100, dtype=int))
        self.assertEqual(result['balanced_accuracy_proxy'], .5)
        self.assertEqual(result['recall_proxy'], 0.)
