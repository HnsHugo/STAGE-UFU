"""Protect original evidence and enforce the explicit recovery population."""
import contextlib
import copy
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import source_cohort as cohort
import source_cohort_recovery as recovery
from test_source_cohort import history, records


class RecoveryTests(unittest.TestCase):
    protocol = Path(__file__).parent/'source_cohort_recovery_protocol_20261029.json'

    def test_real_preparation_preserves_473_complete_entries_without_requests(self):
        _, targets, base, selected = recovery.load(self.protocol)
        self.assertEqual(len(selected),27)
        original = self.protocol.parent/'source_cohort_20261028/batch_0025/checkpoint.json'
        before = original.read_bytes()
        with tempfile.TemporaryDirectory() as folder, patch('prepayment_pilot.get_json',side_effect=AssertionError('No requests')):
            state = recovery.prepare(self.protocol,Path(folder))
            self.assertEqual(len(state['entries']),473)
            self.assertEqual(state['batches'],[])
            self.assertTrue(all(e['status']=='complete' for e in state['entries'].values()))
            for key,entry in state['entries'].items():
                self.assertEqual(entry,base['entries'][key])
            self.assertEqual(recovery.prepare(self.protocol,Path(folder)),state)
        self.assertEqual(original.read_bytes(),before)

    def test_changed_workers_or_target_selection_fail_before_collection(self):
        original=json.loads(self.protocol.read_bytes())
        for edit in ('workers','source_ids','checksum','bounds'):
            changed=copy.deepcopy(original)
            if edit=='workers':changed['workers']=3
            elif edit=='source_ids':changed['recovery']['source_ids']=[]
            elif edit=='checksum':changed['recovery']['original_checkpoint_sha256']='0'*64
            else:changed['max_pages_per_address']=17
            with tempfile.NamedTemporaryFile(dir=self.protocol.parent,suffix='.json') as f:
                Path(f.name).write_bytes(cohort.json_bytes(changed))
                with patch('prepayment_pilot.get_json',side_effect=AssertionError('No requests')):
                    with self.assertRaises(ValueError):recovery.load(Path(f.name))

    def test_complete_source_changes_and_duplicate_attempts_are_rejected(self):
        base=dict(entries={'done':dict(status='complete'), 'gap':dict(status='error')})
        state=dict(entries={'done':dict(status='complete')},batches=[])
        recovery.validate_preservation(state,base,['gap'])
        for bad in [dict(entries={},batches=[]),
                    dict(entries=state['entries'],batches=[dict(source_ids=['done'])]),
                    dict(entries=state['entries'],batches=[dict(source_ids=['gap']),dict(source_ids=['gap'])])]:
            with self.assertRaises(ValueError):recovery.validate_preservation(bad,base,['gap'])

    def test_one_pass_recovery_resumes_without_repeating_attempts(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'protocol.json';path.write_bytes(b'{}')
            protocol=dict(workers=1,default_batch_size=2,reuse_sources=[],recovery=dict(original_checkpoint_sha256='fixture'))
            targets=records(4);base=cohort.empty_state(path,targets)
            for record in targets:
                raw=gzip.compress(cohort.json_bytes(history(record)),mtime=0)
                entry=cohort.from_history(record,history(record),raw,'network')
                if record['pilot_id'] in ('cohort_0002','cohort_0004'):
                    entry=cohort.base_entry(record,'network');entry['reason']='Original timeout'
                base['entries'][record['pilot_id']]=entry
            selected=['cohort_0002','cohort_0004']
            with patch('source_cohort_recovery.load',return_value=(protocol,targets,base,selected)),patch('source_cohort.plan',return_value=(protocol,targets)),patch('source_cohort.helper.fixed.collect_one',side_effect=history) as get,contextlib.redirect_stdout(io.StringIO()):
                first=recovery.run(path,root/'work',root/'out')
                before=(root/'out/batch_0001/checkpoint.json').read_bytes()
                second=recovery.run(path,root/'work',root/'out')
                self.assertEqual(first,second)
                self.assertEqual([c.args[0]['pilot_id'] for c in get.call_args_list],selected)
                self.assertEqual(first['coverage']['complete_sources'],4)
                self.assertTrue(all(r['original_reason']=='Original timeout' for r in first['transitions']))
                self.assertEqual(before,(root/'out/batch_0001/checkpoint.json').read_bytes())

    def test_new_failure_stays_terminal_and_does_not_replace_other_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'protocol.json';path.write_bytes(b'{}')
            protocol=dict(workers=1,default_batch_size=2,reuse_sources=[],recovery=dict(original_checkpoint_sha256='fixture'))
            targets=records(2);base=cohort.empty_state(path,targets)
            base['entries']={r['pilot_id']:cohort.base_entry(r,'network') for r in targets}
            selected=[r['pilot_id'] for r in targets]
            def get(record,proto):
                if record['pilot_id']==selected[0]:raise TimeoutError('Recovery timeout')
                return history(record)
            with patch('source_cohort_recovery.load',return_value=(protocol,targets,base,selected)),patch('source_cohort.plan',return_value=(protocol,targets)),patch('source_cohort.helper.fixed.collect_one',side_effect=get) as fetch,contextlib.redirect_stdout(io.StringIO()):
                result=recovery.run(path,root/'work',root/'out')
                recovery.run(path,root/'work',root/'out')
                self.assertEqual(fetch.call_count,2)
                self.assertEqual(result['coverage']['error_sources'],1)
                self.assertEqual(result['coverage']['pending_sources'],0)


if __name__=='__main__':unittest.main()
