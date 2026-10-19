import unittest
from collect_window import measure, parse_utc


class WindowTests(unittest.TestCase):
    def test_boundaries_and_sender_fees(self):
        rows = [dict(txid=str(i), block_time_utc=date, address_received_sat=10,
                     address_spent_sat=spent, fee_rate_sat_vb=fee)
                for i, (date, spent, fee) in enumerate([
                    ('2026-09-01T00:00:00Z', 0, 999),
                    ('2026-09-02T00:00:00Z', 20, 2),
                    ('2026-09-03T00:00:00Z', 20, 8)])]
        result = measure({'transactions': rows, 'summary': {'coverage': 'count_matches_stable_stats'}},
                         parse_utc('2026-09-01T00:00:00Z'), parse_utc('2026-09-03T00:00:00Z'))
        self.assertEqual(result['metrics']['transaction_count'], 2)
        self.assertEqual(result['metrics']['transactions_per_day'], 1)
        self.assertEqual(result['metrics']['median_spending_fee_rate_sat_vb'], 2)

    def test_missing_is_not_zero(self):
        for coverage in ['partial', 'stats_changed', 'inconsistent_count', 'count_matches_stable_stats']:
            result = measure({'transactions': [], 'summary': {'coverage': coverage}},
                             parse_utc('2026-09-01T00:00:00Z'), parse_utc('2026-09-03T00:00:00Z'))
            if coverage == 'count_matches_stable_stats':
                self.assertEqual(result['metrics']['transaction_count'], 0)
                self.assertIsNone(result['metrics']['median_spending_fee_rate_sat_vb'])
            else:
                self.assertIsNone(result['metrics'])

    def test_explicit_utc_required(self):
        for date in ['2026-09-01', '2026-09-01T00:00:00+02:00']:
            with self.assertRaises(ValueError):
                parse_utc(date)
