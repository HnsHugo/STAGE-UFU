"""Guards for fixed inference, tied metrics and excluded-source preservation."""
from copy import deepcopy
import math
import unittest

import evaluate_cryptobilis_frozen as run

NAMES = ['confirmed_tx_count', 'receipt_tx_count', 'spending_tx_count',
         'received_output_count', 'spent_output_count', 'received_sat', 'spent_sat',
         'balance_sat', 'unspent_output_count', 'active_block_count', 'activity_span_blocks',
         'blocks_since_first_activity', 'blocks_since_last_activity', 'median_spending_tx_fee_rate_sat_vb']


def state():
    return dict(predictor_allowlist=NAMES, model_input_names=NAMES + ['missing__' + n for n in NAMES],
                medians=[7.] * 14, fit_partition='train', fit_rows=1033)


def vector(**changes):
    result = dict.fromkeys(NAMES, 0);result.update(changes)
    return result


def model(threshold=1.):
    return dict(model_input_names=state()['model_input_names'], tree=dict(node_count=3,
        children_left=[1, -1, -1], children_right=[2, -1, -1], feature_indices=[7, -2, -2],
        thresholds=[threshold, -2., -2.], case_membership_score=[.5, .1, .9]))


class InferenceTests(unittest.TestCase):
    def test_frozen_median_and_indicator_are_used(self):
        source = vector(balance_sat=None);original = deepcopy(source);s = state()
        filled, converted, missing = run.transform(source, s)
        self.assertEqual((filled[7], converted[7], converted[21], missing), (7., 7., 1., ['balance_sat']))
        self.assertEqual(source, original);self.assertEqual(s, state())

    def test_zero_is_observed_and_not_imputed(self):
        filled, converted, missing = run.transform(vector(), state())
        self.assertEqual((filled[7], converted[21], missing), (0., 0., []))

    def test_float32_rounding_precedes_tree_branch(self):
        _, converted, _ = run.transform(vector(balance_sat=16777217), state())
        score, leaf, path = run.traverse(model(16777216.5), converted)
        self.assertEqual((converted[7], score, leaf, path), (16777216., .1, 1, [0, 1]))

    def test_equal_split_threshold_goes_left(self):
        _, converted, _ = run.transform(vector(balance_sat=1), state())
        self.assertEqual(run.traverse(model(), converted)[1], 1)

    def test_future_or_label_predictor_is_rejected(self):
        source = vector();source['reported_loss'] = 1
        with self.assertRaisesRegex(ValueError, 'allowlist'):
            run.transform(source, state())

    def test_changed_missing_indicator_order_is_rejected(self):
        s = state();s['model_input_names'] = list(reversed(s['model_input_names']))
        with self.assertRaisesRegex(ValueError, 'indicators changed'):
            run.transform(vector(), s)

    def test_non_training_state_is_rejected(self):
        s = state();s['fit_partition'] = 'external'
        with self.assertRaisesRegex(ValueError, 'training preprocessor'):
            run.transform(vector(), s)

    def test_invalid_values_and_float32_overflow_are_rejected(self):
        for value in [True, '1', math.nan, math.inf, 1e40]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                run.transform(vector(balance_sat=value), state())

    def test_cyclic_or_asymmetric_tree_is_rejected(self):
        _, converted, _ = run.transform(vector(), state())
        for broken in ['cycle', 'leaf']:
            m = model()
            if broken == 'cycle':m['tree']['children_left'][0] = 0
            else:m['tree']['children_right'][1] = 2
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                run.traverse(m, converted)

    def test_wrong_tree_width_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'input width'):
            run.traverse(model(), [0.] * 14)

    def test_tied_average_precision_and_pairwise_auc(self):
        actual = run.metrics([1, 0, 1, 0], [.9, .9, .5, .1])
        self.assertAlmostEqual(actual['average_precision_membership'], 7/12)
        self.assertEqual(actual['roc_auc_membership'], .625)

    def test_constant_baseline_uses_external_prevalence_for_ap(self):
        actual = run.metrics([1, 0, 0], [.3349] * 3)
        self.assertEqual(actual['average_precision_membership'], 1/3)
        self.assertEqual(actual['roc_auc_membership'], .5)
        self.assertNotIn('f1_membership', actual)

    def test_fixed_classification_threshold_is_inclusive(self):
        actual = run.metrics([1, 0], [.5, .49], True)
        self.assertEqual((actual['true_positive_membership'], actual['true_negative_membership'], actual['f1_membership']), (1, 1, 1.))

    def test_all_negative_prediction_keeps_false_negatives(self):
        actual = run.metrics([1, 0], [.1, .2], True)
        self.assertEqual((actual['false_negative_membership'], actual['recall_membership'], actual['f1_membership']), (1, 0., 0.))

    def test_invalid_metric_population_or_score_is_rejected(self):
        for labels, scores in [([1], [.2]), ([1, 0], [.2]), ([1, 0], [math.nan, .1])]:
            with self.subTest(labels=labels), self.assertRaises(ValueError):
                run.metrics(labels, scores)


class EligibilityTests(unittest.TestCase):
    def fixture(self):
        rows, members = [], []
        for i in range(366):
            key = f'source_{i:04d}';label = int(i < 122)
            status = run.ELIGIBLE if i < 275 else 'quarantined_cross_development_component' if i < 329 else 'excluded_bounded_incomplete'
            available = i < 329
            rows.append(dict(source_id=key, cryptobilis_reference_source_membership=label, cutoff_height=970590,
                full_history_status='not_collected_for_this_source', labels=dict(verified_compromise=None),
                incident_group='cryptobilis_2026', features=vector() if available else None,
                precutoff_history_status='complete_prior_prefix' if available else 'bounded_incomplete'))
            members.append(dict(source_id=key, membership=label, cutoff_height=970590,
                full_history_status='not_collected_for_this_source', status=status,
                cross_development_component=275 <= i < 329))
        resume = dict(eligible_source_ids=[r['source_id'] for r in members[:275]],
            quarantined_complete_source_ids=[r['source_id'] for r in members[275:329]],
            bounded_incomplete_source_ids=[r['source_id'] for r in members[329:]])
        return dict(schema_version=2, operational_target=run.TARGET, rows=rows), dict(rows=members), resume

    def test_exact_fixed_selection_and_exclusions_are_retained(self):
        view, manifest, resume = self.fixture()
        _, _, keys = run.eligibility(view, manifest, resume)
        self.assertEqual(len(keys), 275)
        self.assertFalse(set(keys) & set(resume['quarantined_complete_source_ids'] + resume['bounded_incomplete_source_ids']))

    def test_quarantined_component_cannot_be_marked_eligible(self):
        view, manifest, resume = self.fixture();manifest['rows'][0]['cross_development_component'] = True
        with self.assertRaisesRegex(ValueError, 'Quarantined component'):
            run.eligibility(view, manifest, resume)

    def test_bounded_row_cannot_supply_features(self):
        view, manifest, resume = self.fixture();view['rows'][-1]['features'] = vector()
        with self.assertRaisesRegex(ValueError, 'availability mismatch'):
            run.eligibility(view, manifest, resume)

    def test_unknown_label_or_full_history_promotion_is_rejected(self):
        for mutation in ['label', 'history']:
            view, manifest, resume = self.fixture()
            if mutation == 'label':view['rows'][0]['labels']['verified_compromise'] = 1
            else:
                view['rows'][0]['full_history_status'] = manifest['rows'][0]['full_history_status'] = 'complete'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                run.eligibility(view, manifest, resume)

    def test_duplicate_or_replaced_source_is_rejected(self):
        for mutation in ['duplicate', 'replacement']:
            view, manifest, resume = self.fixture()
            if mutation == 'duplicate':view['rows'][1]['source_id'] = view['rows'][0]['source_id']
            else:resume['eligible_source_ids'][0] = 'replacement'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                run.eligibility(view, manifest, resume)


if __name__ == '__main__':
    unittest.main()
