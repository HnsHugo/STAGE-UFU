import unittest
from tune_validation import threshold_results


class ThresholdTests(unittest.TestCase):
    def test_half_score_tie_is_licit(self):
        rows = threshold_results([1, 0], [.5, .5])
        half = next(r for r in rows if r['threshold'] == .5)
        self.assertEqual(half['true_positive'], 0)
        self.assertEqual(half['false_positive'], 0)

    def test_higher_threshold_reduces_alerts(self):
        rows = threshold_results([1, 1, 0, 0], [.9, .6, .7, .2])
        alerts = [r['true_positive'] + r['false_positive'] for r in rows]
        self.assertEqual(alerts, sorted(alerts, reverse=True))


if __name__ == '__main__':
    unittest.main()
