import unittest
import json
import numpy as np
from check_seed_stability import descriptive,summarize_pairs,SEEDS,verify_cache
from analyze_validation_errors import SETTINGS
from grouped_permutation_importance import FAMILIES
from train_source_categories import HASHES


class StabilityTests(unittest.TestCase):
    def test_descriptive_variation_is_not_standard_error(self):
        result=descriptive([1.,2.,3.])
        self.assertAlmostEqual(result['std_ddof0'],np.std([1.,2.,3.]))
        self.assertEqual((result['min'],result['max']),(1.,3.))

    def test_incomplete_or_nonfinite_seeds_rejected(self):
        for values in [[1,2],[1,2,np.nan]]:
            with self.assertRaises(ValueError):descriptive(values)
        with self.assertRaises(ValueError):summarize_pairs([{'seed':43}])

    def test_cached_threshold_change_is_rejected(self):
        settings=json.loads(json.dumps(SETTINGS))
        columns=[c for values in FAMILIES.values() for c in values]
        shared={"versions":{},"membership_sha256":{},"source_sha256":HASHES,
                "threshold_strictly_greater_than":.3}
        reference={**shared,"settings":settings,"features":columns}
        ablation={**shared,"model_settings":settings,"reference_sha256":"verified_digest",
                  "retained_features":[c for c in columns if c not in FAMILIES["monetary"]]}
        verify_cache(reference,ablation,{},"verified_digest")
        ablation["threshold_strictly_greater_than"]=.5
        with self.assertRaises(ValueError):verify_cache(reference,ablation,{},"verified_digest")

    def test_paired_differences_preserve_seed_alignment(self):
        keys=['average_precision','precision','recall','f1','true_positive','false_positive']
        rows=[{'seed':seed,'models':{'full':{'metrics':dict.fromkeys(keys,float(i))},
             'without_monetary':{'metrics':dict.fromkeys(keys,float(i+1))}}}
              for i,seed in enumerate(SEEDS)]
        result=summarize_pairs(rows)['average_precision']['paired_delta_without_minus_full']
        self.assertEqual(result['mean'],1.)
        self.assertEqual(result['std_ddof0'],0.)
