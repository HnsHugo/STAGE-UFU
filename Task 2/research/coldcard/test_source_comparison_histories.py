"""Test durable attempts, source roles, fixed batches and offline restoration."""
import contextlib
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from build_source_registry import digest,json_bytes
import collect_comparison_histories as collect
import source_cohort as saved
from test_source_cohort import history, records


class ComparisonHistoryTests(unittest.TestCase):
    def fixture(self,folder):
        root=Path(folder);path=root/'protocol.json';path.write_bytes(b'{}')
        private=records()
        for i,r in enumerate(private,1):
            r.update(pilot_id=f'comparison_{i:04d}',payment_txid_sha256=digest(r['payment_txid'].encode()),
                     registry_input_slots=1,reference_input_value_sat=60)
        public=[{k:v for k,v in r.items() if k not in ('address','payment_txid')} for r in private]
        protocol=dict(workers=2,default_batch_size=2)
        return root,path,protocol,public,{r['pilot_id']:r for r in private}

    @contextlib.contextmanager
    def mocked(self,fixture,fetch=history):
        root,path,protocol,public,private=fixture
        with patch.object(collect,'private_plan',return_value=(protocol,public,private)),\
             patch.object(collect,'load',return_value=(protocol,public)),\
             patch.object(collect,'bounded_collect_one',side_effect=fetch) as get,\
             contextlib.redirect_stdout(io.StringIO()):yield get

    def test_fixed_batches_resume_without_repeating_sources_and_keep_unknown_labels(self):
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);root,path,_,public,_=f
            with self.mocked(f) as get:
                collect.run_many(path,root/'work',root/'out',1)
                result=collect.run_many(path,root/'work',root/'out',1)
            self.assertEqual(get.call_count,4)
            self.assertEqual(len({c.args[0]['pilot_id'] for c in get.call_args_list}),4)
            self.assertEqual(result['complete_sources'],4)
            state=json.loads((root/'work/state.json').read_bytes())
            for e in state['entries'].values():
                self.assertEqual(e['known_coldcard_core_membership'],0)
                self.assertIsNone(e['compromise_label']);self.assertIsNone(e['hardware_label'])
                self.assertEqual(e['features']['balance_sat'],60)
                self.assertTrue(all(t['height']<20 for t in e['prefix']))

    def test_timeout_and_incomplete_are_retained_without_replacements_or_zero_features(self):
        def fetch(record,protocol):
            if record['pilot_id']=='comparison_0001':raise TimeoutError('bounded fixture')
            data=history(record);data['audit']['pagination_exhausted']=False;return data
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);root,path,_,_,_=f
            with self.mocked(f,fetch) as get:result=collect.run_many(path,root/'work',root/'out',1)
            self.assertEqual(get.call_count,2)
            self.assertEqual((result['error_sources'],result['incomplete_sources'],result['pending_sources']),(1,1,2))
            state=json.loads((root/'work/state.json').read_bytes())
            self.assertTrue(all(e['features'] is None for e in state['entries'].values()))

    def test_started_interrupted_attempt_is_consumed_without_another_http_request(self):
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);root,path,_,public,private=f;work=root/'work'
            state=saved.empty_state(path,public)
            state['batches']=[dict(batch_id=1,source_ids=[r['pilot_id'] for r in public[:2]],status='running')]
            saved.atomic_write(work/'state.json',json_bytes(state))
            saved.atomic_write(work/'attempts/comparison_0001.json',json_bytes(dict(source_id='comparison_0001',started_at='start')))
            with self.mocked(f) as get:result=collect.run_many(path,work,root/'out',1)
            self.assertEqual([c.args[0]['pilot_id'] for c in get.call_args_list],['comparison_0002'])
            self.assertEqual(result['error_types'],{'InterruptedAttempt':1})

    def test_raw_orphan_is_reextracted_without_http_retry(self):
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);root,path,_,public,private=f;work=root/'work'
            state=saved.empty_state(path,public)
            state['batches']=[dict(batch_id=1,source_ids=[r['pilot_id'] for r in public[:2]],status='running')]
            saved.atomic_write(work/'state.json',json_bytes(state))
            saved.atomic_write(work/'attempts/comparison_0001.json',json_bytes(dict(source_id='comparison_0001',started_at='start')))
            saved.atomic_write(work/'raw/comparison_0001.json.gz',gzip.compress(json_bytes(history(private['comparison_0001'])),mtime=0))
            with self.mocked(f) as get:result=collect.run_many(path,work,root/'out',1)
            self.assertEqual(get.call_count,1);self.assertEqual(result['complete_sources'],2)

    def test_changed_reference_input_value_is_an_error_with_raw_evidence_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);record=deepcopy(f[-1]['comparison_0001']);record['reference_input_value_sat']+=1
            raw=gzip.compress(json_bytes(history(record)),mtime=0)
            e=collect.from_raw(record,raw,dict(started_at='start'))
            self.assertEqual(e['status'],'error');self.assertIsNone(e['features'])
            self.assertEqual(e['raw_sha256'],digest(raw))

    def test_offline_restore_needs_no_raw_files_and_does_not_refetch_terminal_entries(self):
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);root,path,_,_,_=f
            with self.mocked(f) as get:
                collect.run_many(path,root/'work',root/'out',2)
                collect.run_many(path,root/'restored',root/'restored_output',1,restore=root/'out/checkpoint.json.gz')
            self.assertEqual(get.call_count,4)
            self.assertFalse((root/'restored/raw').exists())
            self.assertEqual((root/'out/checkpoint.json.gz').read_bytes(),(root/'restored_output/checkpoint.json.gz').read_bytes())

    def test_missing_completed_export_is_repaired_before_next_http(self):
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);root,path,_,_,_=f;out=root/'out'
            with self.mocked(f):collect.run_many(path,root/'work',out,1)
            (out/'batch_0001.json.gz').unlink()
            def get(record,proto):
                self.assertTrue((out/'batch_0001.json.gz').exists());return history(record)
            with self.mocked(f,get):collect.run_many(path,root/'work',out,1)

    def test_export_raw_target_and_feature_tampering_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);root,path,_,public,_=f;work=root/'work';out=root/'out'
            with self.mocked(f):collect.run_many(path,work,out,1)
            state=json.loads((work/'state.json').read_bytes())
            for field,value in [('known_coldcard_core_membership',1),('compromise_label',0),('cutoff_height',21)]:
                changed=deepcopy(state);changed['entries']['comparison_0001'][field]=value
                with self.assertRaises(ValueError):collect.validate(changed,path,public)
            changed=deepcopy(state);changed['entries']['comparison_0001']['features']['balance_sat']+=1
            with self.assertRaises(ValueError):collect.validate(changed,path,public)
            (work/'raw/comparison_0001.json.gz').write_bytes(b'changed')
            with self.mocked(f),self.assertRaises(ValueError):collect.verify(path,out,work)

    def test_a_fully_denied_batch_stops_with_next_sources_pending(self):
        def denied(record,protocol):raise urllib.error.HTTPError('fixture',429,'rate limited',{},None)
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);root,path,_,_,_=f
            with self.mocked(f,denied) as get:result=collect.run_many(path,root/'work',root/'out',2)
            self.assertEqual(get.call_count,2)
            self.assertEqual((result['error_sources'],result['pending_sources']),(2,2))

    def test_https_tunnel_denial_stops_and_a_resume_does_not_issue_new_requests(self):
        def denied(record,protocol):
            raise urllib.error.URLError('Tunnel connection failed: 403 Forbidden')
        with tempfile.TemporaryDirectory() as folder:
            f=self.fixture(folder);root,path,_,_,_=f
            with self.mocked(f,denied) as get:
                result=collect.run_many(path,root/'work',root/'out',2)
                again=collect.run_many(path,root/'work',root/'out',2)
            self.assertEqual(get.call_count,2)
            self.assertEqual(result,again)
            self.assertEqual((result['error_sources'],result['pending_sources']),(2,2))

    def test_real_public_plan_is_fixed_and_contains_no_raw_identifiers(self):
        path=Path(__file__).parent/'source_comparison_collection_protocol_20261030.json'
        _,public=collect.load(path)
        self.assertEqual(len(public),1000)
        self.assertTrue(all('address' not in r and 'payment_txid' not in r for r in public))

    def test_capacity_precheck_avoids_pages_but_never_creates_complete_or_zero_features(self):
        record=dict(address='source',pilot_id='comparison_0001',address_sha256=digest(b'source'),
                    payment_txid='c'*64,payment_txid_sha256=digest(('c'*64).encode()),
                    cutoff_height=20,cutoff_block_hash='f'*64,registry_input_slots=1,reference_input_value_sat=60)
        counters=dict(tx_count=401,funded_txo_count=1,spent_txo_count=1,funded_txo_sum=60,spent_txo_sum=60)
        response=dict(address='source',chain_stats=counters)
        with patch.object(collect.fixed,'get_json',side_effect=[response,deepcopy(response)]) as get:
            data=collect.bounded_collect_one(record,dict(provider='fixture',timeout_seconds=15,max_pages_per_address=16))
        self.assertEqual(get.call_count,2)
        self.assertTrue(all('/txs/' not in c.args[0] for c in get.call_args_list))
        self.assertEqual(data['pages_fetched'],0)
        self.assertFalse(data['audit']['coverage_complete_by_provider_counters'])
        e=collect.from_raw(record,gzip.compress(json_bytes(data)),dict(started_at='start'))
        self.assertEqual(e['status'],'incomplete');self.assertIsNone(e['features'])

    def test_small_history_pagination_uses_same_audit_and_extractor_as_original_collector(self):
        record=records(1)[0];record.update(registry_input_slots=1,reference_input_value_sat=60,
                                         payment_txid_sha256=digest(record['payment_txid'].encode()))
        original=history(record)
        responses=[original['before'],original['transactions'],[],original['after']]
        with patch.object(collect.fixed,'get_json',side_effect=responses):
            data=collect.bounded_collect_one(record,dict(provider='fixture',timeout_seconds=15,max_pages_per_address=16))
        self.assertEqual(data['audit'],original['audit'])
        before=collect.from_raw(record,gzip.compress(json_bytes(original)),dict(started_at='start'))
        after=collect.from_raw(record,gzip.compress(json_bytes(data)),dict(started_at='start'))
        self.assertEqual(before['features'],after['features'])


if __name__=='__main__':unittest.main()
