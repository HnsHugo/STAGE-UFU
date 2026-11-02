"""Checks against held-out preprocessing leakage, tie errors and JSON routing drift."""
from copy import deepcopy
import unittest

import numpy as np
from sklearn.tree import DecisionTreeClassifier

import audit_source_comparison_feasibility as audit
import train_source_membership as train


def row(key, value, label=0):
    return dict(source_id=key, address_sha256=audit.digest(('address:' + key).encode()),
                cutoff_height=100, known_coldcard_core_membership=label,
                precutoff_history_status='complete_full_history', full_history_status='complete',
                features={name: value for name in train.FEATURES})


class PreparationTests(unittest.TestCase):
    def test_heldout_extremes_and_missingness_do_not_affect_training_medians(self):
        fitting = [row('a', 0), row('b', 10), row('c', None)]
        state = train.fit_preprocessing(fitting)
        before = deepcopy(state)
        heldout = [row('heldout', 10**12), row('missing', None)]
        transformed, missing = train.transform(heldout, state)
        self.assertEqual(state, before)
        self.assertEqual(state['medians'], [5.]*14)
        np.testing.assert_array_equal(transformed[1, :14], [5.]*14)
        np.testing.assert_array_equal(transformed[1, 14:], [1.]*14)
        self.assertTrue(missing[1].all())
        self.assertEqual(state['fit_rows'], 3)

    def test_all_missing_training_column_keeps_indicator_and_only_then_uses_zero(self):
        fitting = [row('a', 2), row('b', 4)]
        fitting[0]['features']['balance_sat'] = None
        fitting[1]['features']['balance_sat'] = None
        state = train.fit_preprocessing(fitting)
        self.assertEqual(state['all_missing_training_columns'], ['balance_sat'])
        self.assertEqual(state['medians'][train.FEATURES.index('balance_sat')], 0)
        self.assertEqual(state['medians'][0], 3)
        present, absent = row('zero', 0), row('unknown', 0)
        absent['features']['balance_sat'] = None
        x, _ = train.transform([present, absent], state)
        col = train.FEATURES.index('balance_sat')
        self.assertEqual(x[0, col], x[1, col])
        self.assertEqual((x[0, col+14], x[1, col+14]), (0, 1))

    def test_metadata_cannot_enter_features(self):
        a = row('a', 2)
        a['collection_counter'] = 10**7
        state = train.fit_preprocessing([a])
        self.assertNotIn('collection_counter', state['model_input_names'])
        a['features']['post_cutoff_count'] = 1
        with self.assertRaisesRegex(ValueError, 'allowlist mismatch'):
            train.matrix([a])

    def test_unavailable_source_is_not_silently_imputed(self):
        a = row('unavailable', 1)
        a['features'] = None
        with self.assertRaises((TypeError, ValueError)):
            train.matrix([a])


class ReplayAndMetricTests(unittest.TestCase):
    def test_float32_tree_conversion_and_equality_branch(self):
        model = dict(model_input_names=train.INPUT_NAMES,
                     tree=dict(feature_indices=[0, -2, -2],
                               children_left=[1, -1, -1], children_right=[2, -1, -1],
                               thresholds=[2**24+.5, -2., -2.], case_membership_score=[.5, .1, .9]))
        x = np.zeros((3, 28), dtype=float)
        x[:, 0] = [2**24, 2**24+1, 2**24+2]
        scores, leaves, _ = train.score_export(model, x)
        np.testing.assert_array_equal(leaves, [1, 1, 2])
        np.testing.assert_array_equal(scores, [.1, .1, .9])
        model['tree']['thresholds'][0] = float(2**24)
        self.assertEqual(train.score_export(model, x[:1])[1].tolist(), [1])

    def test_cycles_and_unknown_feature_indices_fail(self):
        model = dict(model_input_names=train.INPUT_NAMES,
                     tree=dict(feature_indices=[0], children_left=[0], children_right=[0],
                               thresholds=[1.], case_membership_score=[.5]))
        with self.assertRaisesRegex(ValueError, 'cyclic'):
            train.score_export(model, np.zeros((1, 28)))
        model['tree']['feature_indices'][0] = 28
        with self.assertRaisesRegex(ValueError, 'Disallowed'):
            train.score_export(model, np.zeros((1, 28)))

    def test_threshold_half_is_included_even_when_argmax_would_choose_zero(self):
        result = train.metrics([0, 1], [.5, .5], classify=True)
        self.assertEqual(result['true_positive_membership'], 1)
        self.assertEqual(result['false_positive_membership'], 1)
        self.assertEqual(result['false_negative_membership'], 0)
        self.assertEqual(result['f1_membership'], 2/3)

    def test_tie_group_ap_and_pairwise_auc_match_hand_calculation(self):
        for y, scores, ap, auc in [([0, 1, 1, 0], [.1, .8, .8, .8], 2/3, .75),
                                    ([0, 1, 0, 1], [.5]*4, .5, .5),
                                    ([0, 1], [.9, .1], .5, 0.),
                                    ([0, 1], [.1, .9], 1., 1.)]:
            independent = train.independent_ranking(y, scores)
            self.assertAlmostEqual(independent['average_precision_membership'], ap)
            self.assertAlmostEqual(independent['roc_auc_membership'], auc)
            sklearn_metrics = train.metrics(y, scores)
            for key, value in independent.items():
                self.assertAlmostEqual(sklearn_metrics[key], value)

    def test_fitted_synthetic_tree_replays_as_inert_json(self):
        rows = [row(str(i), i//30, int(i >= 30)) for i in range(90)]
        state = train.fit_preprocessing(rows)
        x, _ = train.transform(rows, state)
        fitted = DecisionTreeClassifier(max_depth=3, min_samples_leaf=20,
                                        class_weight='balanced', random_state=42).fit(x, [r[train.TARGET] for r in rows])
        model = train.export_tree(fitted, state, dict(input_commit='synthetic-test'))
        scores, leaves, _ = train.score_export(model, x)
        np.testing.assert_array_equal(scores, fitted.predict_proba(x)[:, 1])
        np.testing.assert_array_equal(leaves, fitted.apply(x))
        self.assertEqual(model['fit_partition'], 'train')
        self.assertFalse(model['test_used_for_selection'])


class FrozenSplitTests(unittest.TestCase):
    def test_audited_component_membership_and_missing_exclusion_are_preserved(self):
        # Synthetic component graph: find enough singletons in all frozen buckets.
        rows = [row(str(i), i, i % 2) for i in range(3000)]
        selected, counts = [], {p: dict(case=0, comparison=0, components=0) for p in train.PARTS}
        for r in rows:
            part = audit.partition_for(r['address_sha256'])
            label = 'case' if r[train.TARGET] else 'comparison'
            if counts[part][label] < 20:
                selected.append(r)
                counts[part][label] += 1
                counts[part]['components'] += 1
        self.assertTrue(all(c[k] == 20 for c in counts.values() for k in ('case', 'comparison')))
        groups = dict(components=[dict(source_ids=[r['source_id']],
                                       component_id=audit.digest(audit.json_bytes([r['source_id']])),
                                       minimum_address_sha256=r['address_sha256']) for r in selected],
                      shared_link_evidence={})
        absent = row('excluded', 0)
        absent['features'] = None
        absent['precutoff_history_status'] = 'bounded_incomplete'
        absent['full_history_status'] = 'incomplete'
        split = train.frozen_split(dict(rows=selected+[absent]), groups,
                                   dict(frozen_partition_feasibility=dict(counts=counts)))
        self.assertEqual(split['excluded_sources'], 1)
        excluded = next(r for r in split['rows'] if r['source_id'] == 'excluded')
        self.assertEqual(excluded['partition'], 'excluded_unavailable_prefix')
        self.assertIsNone(excluded['component_id'])
        groups['components'][0]['minimum_address_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'identity changed'):
            train.frozen_split(dict(rows=selected+[absent]), groups,
                               dict(frozen_partition_feasibility=dict(counts=counts)))


if __name__ == '__main__':
    unittest.main()
