import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from native_fifty_page_campaign import ADDITIONAL_PAGES, MAX_UNIT_SOURCES, build_units, request_budget

B = Path(__file__).resolve().parent


class FiftyPageContinuationTests(unittest.TestCase):
    def test_fifty_pages_budget_includes_both_anchors_and_funding(self):
        budget = request_budget([{'registry_input_slots': 2}, {'registry_input_slots': 3}])
        self.assertEqual(ADDITIONAL_PAGES, 50)
        self.assertEqual(budget['tail_pages_at_most'], 100)
        self.assertEqual(budget['total_new_requests_at_most'], 109)

    def test_larger_extensions_use_small_uniform_frontier_units(self):
        queue = [dict(source_id=f'{bound}_{i:02d}', native_pages=bound)
                 for bound, n in [(112, 2), (128, 13), (144, 3)] for i in range(n)]
        ids = [r['source_id'] for r in queue]
        units = build_units({'retained_native_partial_queue': queue}, ids)
        self.assertEqual(MAX_UNIT_SOURCES, 3)
        self.assertEqual([len(u) for u in units], [2, 3, 3, 3, 3, 1, 3])
        self.assertEqual(sum(units, []), ids)
        bounds = {r['source_id']: r['native_pages'] for r in queue}
        self.assertTrue(all(len({bounds[s] for s in u}) == 1 for u in units))

    def test_legacy_campaign_rejected_before_any_mutation(self):
        p = B / 'mempool_native_round5_20261115/progress.json'
        before = p.read_bytes()
        result = subprocess.run([sys.executable, str(B / 'native_fifty_page_campaign.py'),
                                 'mempool_native_round5_20261115', 'init'], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(before, p.read_bytes())

    def test_previous_driver_still_matches_published_protocol_pin(self):
        out = B / 'mempool_native_round5_20261115_unit_01'
        q = json.loads((out / 'protocol.json').read_text())
        pin = q['inputs']['checkpoint_code']
        self.assertEqual(hashlib.sha256((out / pin['file']).read_bytes()).hexdigest(), pin['sha256'])


if __name__ == '__main__':
    unittest.main()
