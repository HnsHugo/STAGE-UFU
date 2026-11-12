"""Guard contracts for explicit recovery of previously unavailable response bodies."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from prepare_frontier_checkpoint import choose_sources
from run_frontier_checkpoint import verify_recovered_response


class RecoveryContracts(unittest.TestCase):
    def setUp(self):
        self.expected = dict(source_id='comparison_0241', key='tail_0000', sha256='old-body', endpoint_sha256='old-cursor')
        self.marker = dict(self.expected, http_status=200)

    def test_exact_reacquisition_accepted_and_changed_body_or_cursor_rejected(self):
        verify_recovered_response(self.expected, self.marker)
        for field in ['sha256', 'endpoint_sha256', 'source_id', 'key']:
            with self.subTest(field=field):
                changed = dict(self.marker, **{field: 'changed'})
                with self.assertRaises(ValueError):
                    verify_recovered_response(self.expected, changed)

    def test_recovery_cannot_be_fabricated_by_missing_body_or_offline_flag(self):
        for update in [dict(sha256=None), dict(http_status=429), dict(offline_reused=True)]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                verify_recovered_response(self.expected, dict(self.marker, **update))

    def test_fixed_order_excludes_retained_deep_sources_and_complete_rows(self):
        ids = ['comparison_0241', 'comparison_0249']
        resume = dict(coldcard_unextended_at_16_page_bound_source_ids=ids, source_ids=['comparison_0157'])
        view = dict(rows=[dict(source_id=sid, features=None) for sid in ids])
        restored = dict(next_twenty_source_ids=ids)
        self.assertEqual(choose_sources(resume, view, restored)[0], ids)
        changed = copy.deepcopy(view)
        changed['rows'][0]['features'] = {'vector': 1}
        with self.assertRaises(AssertionError):
            choose_sources(resume, changed, restored)
        with self.assertRaises(AssertionError):
            choose_sources(dict(resume, source_ids=[ids[0]]), view, restored)
        with self.assertRaises(AssertionError):
            choose_sources(dict(resume, coldcard_unextended_at_16_page_bound_source_ids=ids[::-1]), view, restored)

    def test_real_prepared_protocol_passes_original_eight_control_loader_without_http(self):
        import collect_reference_tail_many as many
        root = Path(__file__).resolve().parent
        scope = root / 'source_prefix_extension_20261112_02'
        with patch.object(many.tail, 'run') as runner, patch.object(many, 'verify', return_value=0):
            many.main(scope / 'protocol.json', scope, root / ('source_cohort_work_' + scope.name))
            runner.assert_called_once()


if __name__ == '__main__':
    unittest.main()
