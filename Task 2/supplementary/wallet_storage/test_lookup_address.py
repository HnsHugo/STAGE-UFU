"""Offline checks of the API boundary; these are synthetic responses."""
import unittest
from lookup_address import normalize


class LookupTests(unittest.TestCase):
    def test_unnamed_cluster_is_found(self):
        result = normalize({'found': True, 'wallet_id': 'abc', 'updated_to_block': 123})
        self.assertEqual(result['lookup_status'], 'found')
        self.assertIsNone(result['service_label'])

    def test_unknown_address_is_not_an_error_or_label(self):
        result = normalize({'found': False})
        self.assertEqual(result['lookup_status'], 'not_found')
        self.assertIsNone(result['wallet_id'])

    def test_errors_and_malformed_responses_are_rejected(self):
        for payload in ({'error': 'bad address'}, {}, {'found': 'false'},
                        {'found': True}, [], {'found': True, 'wallet_id': 123}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                normalize(payload)


if __name__ == '__main__':
    unittest.main()
