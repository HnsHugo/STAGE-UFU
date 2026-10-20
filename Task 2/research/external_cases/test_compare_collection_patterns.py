import json
from pathlib import Path
import tempfile
import unittest

from compare_collection_patterns import busiest_day, compare, day_start
from test_collection_patterns import tx


class ComparisonTests(unittest.TestCase):
    def test_schema2_rejects_incident_and_comparison_in_same_split_group(self):
        root = Path(__file__).resolve().parent/'collection_comparison_20261019'
        registry = json.loads((root/'registry.json').read_text())
        registry['schema_version'] = 2
        for record in registry['records']:
            record['history_file'] = str((root/record['history_file']).resolve())
        registry['records'][-1]['group'] = registry['records'][0]['group']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'registry.json'
            path.write_text(json.dumps(registry))
            with self.assertRaisesRegex(ValueError, 'both an incident and comparison'):
                compare(path)

    @unittest.skipUnless((Path(__file__).resolve().parent/'fsf_history_20261014.json.gz').exists(),
                         'Separately supplied FSF history required for expanded-cohort reproduction')
    def test_expanded_pinned_cohort_reproduces_without_changing_previous_rows(self):
        root = Path(__file__).resolve().parent
        old = json.loads((root/'collection_comparison_20261019/comparison.json').read_text())
        expected = json.loads((root/'collection_expanded_20261020/comparison.json').read_text())
        actual = compare(root/'collection_expanded_20261020/registry.json')
        self.assertEqual(actual, expected)
        self.assertEqual(actual['rows'][:len(old['rows'])], old['rows'])
        self.assertEqual(actual['group_summary'], dict(incident_groups=2, comparison_entities=2,
                                                     address_count=5, observation_windows=9))

    def test_stress_window_ties_choose_earliest_day_not_input_order(self):
        recent = tx('a', when=day_start('2026-10-09'))
        early = tx('b', when=day_start('2026-07-30'))
        self.assertEqual(busiest_day('collector', [recent, early], day_start('2026-10-10')), '2026-07-30')

    def test_future_receipts_do_not_select_stress_window(self):
        early = tx('a', when=day_start('2026-07-30'))
        future = [tx(str(i), when=day_start('2026-10-10')) for i in range(3)]
        self.assertEqual(busiest_day('collector', [early]+future, day_start('2026-10-10')), '2026-07-30')

    def test_no_receipts_does_not_invent_a_window(self):
        with self.assertRaises(ValueError):
            busiest_day('collector', [], day_start('2026-10-10'))

    def test_pinned_result_reproduces_and_preserves_groups(self):
        root = Path(__file__).resolve().parent
        expected = json.loads((root/'collection_comparison_20261019/comparison.json').read_text())
        actual = compare(root/'collection_comparison_20261019/registry.json')
        self.assertEqual(expected, actual)
        self.assertEqual(len(actual['rows']), 6)
        self.assertEqual(len({r['group'] for r in actual['rows']}), 3)
        self.assertEqual(len({r['group'] for r in actual['rows'] if r['context']=='incident'}), 2)
        self.assertTrue(all(r['window_seconds']==86400 for r in actual['rows']))
        self.assertTrue(all(r['hardware_control']=='unknown' for r in actual['rows']))

    def test_changed_raw_bytes_fail_before_analysis(self):
        root = Path(__file__).resolve().parent/'collection_comparison_20261019'
        registry = json.loads((root/'registry.json').read_text())
        for record in registry['records']:
            record['history_file'] = str((root/record['history_file']).resolve())
        registry['records'][0]['history_sha256'] = '0'*64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'registry.json'
            path.write_text(json.dumps(registry))
            with self.assertRaisesRegex(ValueError, 'checksum'):
                compare(path)


if __name__ == '__main__':
    unittest.main()
