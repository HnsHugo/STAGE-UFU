import unittest
import numpy as np
from grouped_permutation_importance import permute_family,validate_families,FAMILIES


class PermutationTests(unittest.TestCase):
    def test_joint_dependencies_preserved_and_source_unmodified(self):
        data=np.array([[1.,2.,99.],[3.,6.,98.],[4.,8.,97.]])
        before=data.copy()
        shuffled=permute_family(data,[0,1],np.array([2,0,1]))
        np.testing.assert_array_equal(shuffled[:,1],2*shuffled[:,0])
        np.testing.assert_array_equal(shuffled[:,2],before[:,2])
        np.testing.assert_array_equal(data,before)

    def test_identity_is_noop(self):
        data=np.arange(6).reshape(3,2)
        np.testing.assert_array_equal(permute_family(data,[0,1],np.arange(3)),data)

    def test_duplicate_permutation_and_incomplete_schema_rejected(self):
        with self.assertRaises(ValueError):permute_family(np.zeros((3,2)),[0],np.array([0,0,1]))
        columns=[c for values in FAMILIES.values() for c in values]
        validate_families(columns)
        with self.assertRaises(ValueError):validate_families(columns[:-1])
