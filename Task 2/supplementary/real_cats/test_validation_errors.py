import unittest
import numpy as np
from analyze_validation_errors import diagnose


class DiagnosticTests(unittest.TestCase):
    def test_categories_and_missingness_do_not_change_confusion(self):
        result = diagnose(['benign','benign','Hack','Theft'], [0,1,0,1],
                          np.array([[0,0],[1,0],[0,1],[1,1]], dtype=bool))
        self.assertEqual(result['outcomes'], {'TP':1,'FN':1,'FP':1,'TN':1})
        self.assertEqual(result['missing_by_outcome']['TP']['missing_cells_by_feature'], [1,1])
        for category in ['benign','Hack','Theft']:
            rows = [r for r in result['strata'] if r['source_category'] == category]
            self.assertEqual(rows[0]['count'], rows[1]['count'] + rows[2]['count'])

    def test_absent_category_rate_is_null_not_zero(self):
        result = diagnose(['benign'], [0], np.zeros((1,2), dtype=bool))
        self.assertTrue(all(r['alert_rate'] is None for r in result['strata'] if r['count']==0))

    def test_unknown_category_and_shape_mismatch_rejected(self):
        with self.assertRaises(ValueError): diagnose(['unknown'], [0], np.zeros((1,2)))
        with self.assertRaises(ValueError): diagnose(['Hack'], [], np.zeros((1,2)))
