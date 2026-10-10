import unittest
from collect_theft_seeds import validate_address, check_history

ADDRESS = '3LU8wRu4ZnXP4UM8Yo6kkTiGHM9BubgyiG'


class CollectionTests(unittest.TestCase):
    def test_checksum_rejects_transcription_error(self):
        validate_address(ADDRESS)
        with self.assertRaises(ValueError):
            validate_address(ADDRESS[:-1] + 'H')

    def fixtures(self):
        stats = dict(chain_stats=dict(tx_count=1, funded_txo_count=1,
                     spent_txo_count=0, funded_txo_sum=123, spent_txo_sum=0))
        tx = dict(txid='a' * 64, status=dict(confirmed=True, block_hash='b' * 64),
                  vin=[], vout=[dict(scriptpubkey_address=ADDRESS, value=123)])
        return stats, tx

    def test_complete_requires_exhaustion_and_matching_amounts(self):
        stats, tx = self.fixtures()
        self.assertTrue(check_history(ADDRESS, [tx], stats, stats, True)['coverage_complete_by_provider_counters'])
        self.assertFalse(check_history(ADDRESS, [tx], stats, stats, False)['coverage_complete_by_provider_counters'])
        tx['vout'][0]['value'] = 124
        self.assertFalse(check_history(ADDRESS, [tx], stats, stats, True)['coverage_complete_by_provider_counters'])

    def test_duplicates_and_unrelated_transactions_rejected(self):
        stats, tx = self.fixtures()
        with self.assertRaises(ValueError):
            check_history(ADDRESS, [tx, tx], stats, stats, True)
        tx['vout'] = []
        with self.assertRaises(ValueError):
            check_history(ADDRESS, [tx], stats, stats, True)

    def test_changed_provider_counters_are_incomplete(self):
        stats, tx = self.fixtures()
        changed = dict(chain_stats=dict(stats['chain_stats'], tx_count=2))
        self.assertFalse(check_history(ADDRESS, [tx], stats, changed, True)['coverage_complete_by_provider_counters'])


if __name__ == '__main__':
    unittest.main()
