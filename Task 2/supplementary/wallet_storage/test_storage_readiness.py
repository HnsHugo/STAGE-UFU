import copy
import hashlib
import unittest
from audit_storage_readiness import assess, label_covers_window, utc, verify_input


def document():
    return {'seed': {'address': 'public-address', 'entity_name': 'synthetic',
                    'purpose': 'research_sample', 'storage_type': 'cold',
                    'storage_source_url': 'https://example.test/evidence'},
            'storage_label_window_validity': 'verified',
            'storage_label_evidence': {'source_url': 'https://example.test/evidence',
                'valid_from_utc': '2026-09-01T00:00:00Z',
                'valid_until_utc_exclusive': '2026-10-01T00:00:00Z',
                'published_at_utc': '2026-09-01T00:00:00Z'},
            'window': {'start_utc_inclusive': '2026-09-01T00:00:00Z',
                'end_utc_exclusive': '2026-10-01T00:00:00Z',
                'window_coverage': 'count_consistent_full_history',
                'metrics': {'transaction_count': 0}}}


class EligibilityTests(unittest.TestCase):
    def test_newline_identity_is_explicit_and_content_changes_rejected(self):
        digest = hashlib.sha256(b"a,b\r\nc,d\r\n").hexdigest()
        self.assertEqual(verify_input(b"a,b\r\nc,d\r\n", digest), "exact_bytes")
        self.assertIn("reconstruction", verify_input(b"a,b\nc,d\n", digest))
        with self.assertRaises(ValueError): verify_input(b"a,b\nx,d\n", digest)

    def test_covered_zero_is_retained(self):
        row = assess(document())
        self.assertTrue(row['eligible'])
        self.assertEqual(row['window_transaction_count'], 0)

    def test_truncated_zero_remains_missing(self):
        doc = document(); doc['window']['window_coverage'] = 'unverified'
        row = assess(doc)
        self.assertFalse(row['eligible'])
        self.assertIsNone(row['window_transaction_count'])

    def test_unknown_and_smoke_test_are_excluded(self):
        for field, value in [('storage_type', 'unknown'), ('purpose', 'api_smoke_test')]:
            doc = document(); doc['seed'][field] = value
            self.assertFalse(assess(doc)['eligible'])

    def test_snapshot_and_late_publication_do_not_cover_window(self):
        for field, value in [('valid_until_utc_exclusive', '2026-09-01T00:00:00Z'),
                             ('published_at_utc', '2026-10-02T00:00:00Z')]:
            doc = document(); doc['storage_label_evidence'][field] = value
            self.assertFalse(label_covers_window(doc))

    def test_review_date_or_verified_flag_alone_is_insufficient(self):
        doc = document(); del doc['storage_label_evidence']
        doc['seed']['reviewed_at_utc'] = '2026-09-01T00:00:00Z'
        self.assertFalse(label_covers_window(doc))

    def test_timezone_and_wrong_source_rejected(self):
        with self.assertRaises(ValueError): utc('2026-09-01T00:00:00')
        doc = copy.deepcopy(document())
        doc['storage_label_evidence']['source_url'] = 'https://example.test/other'
        self.assertFalse(label_covers_window(doc))


if __name__ == '__main__': unittest.main()
