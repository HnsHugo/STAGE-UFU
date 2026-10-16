import unittest

from course_baseline import TARGET, choose_cohort, keep_smallest, row_from_tx


class CourseBaselineTests(unittest.TestCase):
    def test_exact_course_features_use_output_values_and_population_std(self):
        tx = dict(hash='a', size=150, weight=600, fee=10,
                  inputs=[dict(prev_out=dict(tx_index=2, n=0, value=50))],
                  out=[dict(addr=TARGET, value=10), dict(addr='other', value=30)])
        row = row_from_tx(12, tx)
        self.assertTrue(row['pays_course_address'])
        self.assertEqual([row[k] for k in ['output_sum_sat','output_min_sat',
                         'output_max_sat','output_mean_sat','output_std_sat']],
                         [40, 10, 30, 20, 10])
        tx['inputs'][0]['prev_out'] = dict(tx_index=0, n=4294967295)
        self.assertIsNone(row_from_tx(12, tx))

    def test_cohort_matches_blocks_and_is_independent_of_stream_order(self):
        positives = [dict(txid='p'+str(i), block_height=i % 2) for i in range(8)]
        negatives = [dict(txid='n'+str(i), block_height=i % 2) for i in range(30)]
        def select(sequence):
            heaps = {}
            for row in sequence:
                keep_smallest(heaps.setdefault(row['block_height'], []), row, 4)
            return choose_cohort(positives, heaps, 4)
        a, b = select(negatives), select(reversed(negatives))
        self.assertEqual(a, b)
        self.assertEqual(len({r['txid'] for r in a}), 8)
        for h in [0, 1]:
            self.assertEqual(sum(r['block_height']==h and r['txid'].startswith('p') for r in a),
                             sum(r['block_height']==h and r['txid'].startswith('n') for r in a))

    def test_insufficient_matched_background_is_rejected(self):
        with self.assertRaises(ValueError):
            choose_cohort([dict(txid='p', block_height=1)], {}, 1)


if __name__ == '__main__':
    unittest.main()
