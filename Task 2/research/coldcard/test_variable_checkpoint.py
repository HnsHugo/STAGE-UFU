"""Offline accounting tests with isolated synthetic post-audit fixtures.

Raw extraction and the preceding export audit are assumed by this component.
No fixture is a research result, and no provider transport is imported.
"""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import finalize_variable_checkpoint as finalizer


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, sort_keys=True) + '\n').encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VariableCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ufu-finalizer-test-')
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.parent, self.out = base/'parent', base/'successor'
        self.work = base/'source_cohort_work_successor'
        self.rows = [dict(source_id=f'control_{i:04d}', features={'count':1}, cutoff_height=20) for i in range(1499)]
        self.rows.append(dict(source_id='target', features=None, cutoff_height=20))
        self.old_transactions = [dict(txid='old', status={'block_height':10})]
        self.new_transactions = self.old_transactions + [dict(txid='new', status={'block_height':11})]
        write(self.parent/'precutoff_feature_view.json.gz', {'rows':self.rows})
        write(self.parent/'checkpoint.json.gz', {'entries':{}})
        write(self.parent/'resume_checkpoint.json', {'coldcard_unextended_at_16_page_bound_source_ids':[]})
        self.protocol = dict(parent_scope='parent', source_ids=['target'], baseline_vectors=1499,
            previous_bound=384, per_source_saved_pages={'target':440}, max_pages_per_address=448)
        write(self.out/'protocol.json', self.protocol)
        write(self.out/'independent_verification.json', {'status':'passed'})
        write(self.out/'resume_checkpoint.json', {'status':'prepared_not_started'})

    def fixture(self, status='bounded_incomplete', fresh_page=440, changed_prefix=False):
        after = copy.deepcopy(self.rows)
        transactions = copy.deepcopy(self.new_transactions)
        if changed_prefix:
            transactions[0]['txid'] = 'changed-old-prefix'
        raw = self.work/'raw/target.json.gz'
        write(raw, {'transactions':transactions})
        features = {'count':2} if status == 'complete_prior_prefix' else None
        if status == 'complete_prior_prefix':
            after[-1]['features'] = features
        entries = {} if status == 'pending' else {'target':dict(status=status,
            features=features, pages_fetched=448, raw_file='raw/target.json.gz', raw_sha256=digest(raw))}
        write(self.out/'checkpoint.json.gz', dict(protocol_sha256=digest(self.out/'protocol.json'), entries=entries))
        write(self.out/'precutoff_feature_view.json.gz', {'rows':after})
        pending = [dict(source_id='target', saved_tail_pages=443)] if status == 'pending' else []
        write(self.out/'coverage_audit.json', {'pending_source_page_checkpoints':pending})
        write(self.out/'request_manifest.json.gz', [dict(source_id='target', key=f'tail_{fresh_page:04d}', http_status=200)])

    def run_finalizer(self):
        with patch.object(finalizer, 'load_parent_evidence',
                          return_value=({'transactions':self.old_transactions}, {'pages_fetched':440})):
            return finalizer.finalize(self.out)

    def test_completed_source_counts_only_observations_after_partial_parent(self):
        self.fixture(status='complete_prior_prefix')
        report = self.run_finalizer()
        self.assertEqual(report['coldcard_vectors'], 1500)
        self.assertEqual(report['new_complete_prefixes'], 1)
        self.assertEqual(report['additional_source_transaction_observations'], 1)
        detail = finalizer.read(self.out/'continuation_reconciliation.json')['source_progress'][0]
        self.assertEqual(detail['previous_pages'], 440)
        self.assertEqual(finalizer.read(self.out/'precutoff_feature_view.json.gz')['rows'][:-1], self.rows[:-1])

    def test_bounded_source_retains_null_features_and_continuation(self):
        self.fixture()
        report = self.run_finalizer()
        self.assertEqual(report['coldcard_vectors'], 1499)
        self.assertEqual(report['new_complete_prefixes'], 0)
        resume = finalizer.read(self.out/'resume_checkpoint.json')
        self.assertEqual(resume['continuation_required_source_ids'], ['target'])
        self.assertEqual(resume['continuation_queue'][0]['saved_pages'], 448)
        self.assertIsNone(finalizer.read(self.out/'precutoff_feature_view.json.gz')['rows'][-1]['features'])

    def test_another_interruption_preserves_the_partial_cursor(self):
        self.fixture(status='pending')
        report = self.run_finalizer()
        self.assertEqual(report['status'], 'partial_checkpoint')
        self.assertEqual(report['coldcard_vectors'], 1499)
        self.assertEqual(report['pending_source_ids'], ['target'])
        resume = finalizer.read(self.out/'resume_checkpoint.json')
        self.assertEqual(resume['continuation_queue'][0]['saved_pages'], 443)
        self.assertFalse(resume['restart_same_scope_allowed'])

    def test_replay_below_this_source_bound_is_rejected(self):
        self.fixture(fresh_page=439)
        with self.assertRaises(AssertionError):
            self.run_finalizer()
        self.assertFalse((self.out/'continuation_reconciliation.json').exists())

    def test_changed_original_transactions_are_rejected(self):
        self.fixture(changed_prefix=True)
        with self.assertRaises(AssertionError):
            self.run_finalizer()
        self.assertFalse((self.out/'continuation_reconciliation.json').exists())


if __name__ == '__main__':
    unittest.main()
