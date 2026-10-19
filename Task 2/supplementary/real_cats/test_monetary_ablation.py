import unittest
import numpy as np
from ablate_monetary_features import retained_features,summarize_categories
from grouped_permutation_importance import FAMILIES


class AblationTests(unittest.TestCase):
    def test_exact_family_removed_without_mutating_schema(self):
        columns=[c for values in FAMILIES.values() for c in values]
        before=columns.copy()
        retained=retained_features(columns)
        self.assertEqual(columns,before)
        self.assertEqual(len(retained),13)
        self.assertFalse(set(retained)&set(FAMILIES['monetary']))
        self.assertIn('transaction_fee',retained)

    def test_unknown_schema_rejected(self):
        with self.assertRaises(ValueError):retained_features(['balance','unreviewed_feature'])

    def test_category_counts_and_alerts(self):
        observed=summarize_categories(np.array(['Hack','Hack','Theft','benign']),np.array([1,0,1,0]))
        self.assertEqual(observed['Hack'],{'count':2,'alerts':1})
        self.assertEqual(sum(row['alerts'] for row in observed.values()),2)
