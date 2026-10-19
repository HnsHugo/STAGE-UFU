import unittest
from probe_blockcypher import validate


class ProbeTests(unittest.TestCase):
    def test_strict_height_bounds_and_empty_not_proof(self):
        self.assertEqual(validate({'address': 'a'}, 'a', 100)['filter_observation'], 'empty_inconclusive')
        result = validate({'address': 'a', 'txrefs': [{'block_height': h} for h in [90, 91, 99, 100]]},
                          'a', 100, 90)
        self.assertEqual(result['out_of_bounds_references'], 2)
        self.assertEqual(result['filter_observation'], 'violated')
        with self.assertRaises(ValueError):
            validate({'address': 'other'}, 'a', 100)
