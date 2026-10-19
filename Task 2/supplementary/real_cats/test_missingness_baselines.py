import unittest
import numpy as np
import pandas as pd
from compare_missingness_baselines import missing_indicators, fit_baseline, evaluate


class MissingnessBaselineTests(unittest.TestCase):
    def test_values_removed_and_nonfinite_coerced(self):
        frame = pd.DataFrame({'a':[1,999,np.nan], 'b':['bad',np.inf,-np.inf]})
        np.testing.assert_array_equal(missing_indicators(frame), [[0,1],[0,1],[1,1]])
        frame.loc[0,'a'] = -123456
        np.testing.assert_array_equal(missing_indicators(frame), [[0,1],[0,1],[1,1]])

    def test_continuous_features_cannot_be_supplied(self):
        with self.assertRaises(ValueError): fit_baseline([[.1],[1]], [0,1], False)

    def test_no_information_baseline_has_prevalence_ap(self):
        result = evaluate(np.array([0,0,0,1]), np.full(4, .25))
        self.assertEqual(result['average_precision'], .25)
        self.assertEqual(result['alert_count'], 0)

    def test_strict_threshold_excludes_exact_half(self):
        result = evaluate(np.array([0,1]), np.array([.5,.5]))
        self.assertEqual(result['true_positive'], 0)
        self.assertEqual(result['false_positive'], 0)
