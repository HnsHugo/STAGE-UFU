"""Protect closed campaigns and selection of genuinely resumable native tails."""
import unittest
from native_extension_checkpoint import choose_sources, request_budget


class NativeExtensionTests(unittest.TestCase):
    def test_selection_excludes_complete_wrong_bound_and_mixed_seeds(self):
        queue = [dict(source_id=s, seed_kind=k, native_pages=n) for s,k,n in
                 [('b','native',48),('a','native',48),('done','native',48),
                  ('bridge','bridge_union',48),('other','native',32)]]
        rows = {x['source_id']: {'features': None} for x in queue}
        rows['done']['features'] = {'known': 1}
        self.assertEqual(choose_sources({'retained_native_partial_queue': queue}, rows), ['a','b'])

    def test_duplicate_queue_rejected(self):
        item = dict(source_id='a', seed_kind='native', native_pages=48)
        with self.assertRaises(ValueError):
            choose_sources({'retained_native_partial_queue': [item,item]}, {'a': {'features': None}})

    def test_fixed_limit_is_deterministic(self):
        queue = [dict(source_id=str(i), seed_kind='native', native_pages=48) for i in reversed(range(9))]
        self.assertEqual(choose_sources({'retained_native_partial_queue': queue},
                         {str(i): {'features': None} for i in range(9)}), list('01234'))

    def test_budget_allows_funding_checks_without_requerying_old_pages(self):
        b = request_budget([{'registry_input_slots': 3}, {'registry_input_slots': 1}])
        self.assertEqual(b, dict(before_statuses_at_most=2, tail_pages_at_most=32,
                         after_anchor_statuses_at_most=2, funding_statuses_at_most=4,
                         total_new_requests_at_most=40))


if __name__ == '__main__': unittest.main()
