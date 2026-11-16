from copy import deepcopy
from datetime import datetime,timedelta,timezone
import gzip
import hashlib
from pathlib import Path
import tempfile
import unittest

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read,sha,write
from planned_funding_bridge import collect,legacy_source,funding_plan
from audit_planned_funding_bridge import audit
from test_independent_mempool_bridge import tx
from independent_mempool_pilot import PROVIDER


class PlannedFundingTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.work=Path(temporary.name);self.record=dict(pilot_id='s',address='source',payment_txid='reference',
            cutoff_height=10,cutoff_block_hash='block-10',registry_input_slots=1,reference_input_value_sat=10)
        for name in ['legacy/s','raw','results']:(self.work/name).mkdir(parents=True)
        anchor=tx('reference',10);anchor['vin']=[dict(txid='same-block-fund',vout=0,prevout=dict(scriptpubkey_address='source',value=10))]
        self.anchor=anchor;self.old=[tx('newer',8),tx('boundary',5)]
        self.pins={}
        for key,endpoint,data in [('reference','/tx/reference',anchor),('tail_0000','/address/source/txs/chain/reference',self.old)]:
            folder=self.work/'legacy/s';body=folder/(key+'.json.gz');body.write_bytes(gzip.compress(json_bytes(data),mtime=0))
            m=dict(source_id='s',key=key,http_status=200,sha256=sha(body),endpoint_sha256=hashlib.sha256(endpoint.encode()).hexdigest())
            write(folder/(key+'.json'),m);self.pins[key]=m
        self.plan={'s':funding_plan(self.record,anchor,self.old)};write(self.work/'legacy_funding_plan.json',self.plan)
        self.q=dict(private_legacy_funding_plan_sha256=sha(self.work/'legacy_funding_plan.json'),maximum_new_native_pages=2)

    def responses(self,parent_height=10,record_markers=False):
        outer=self
        class Responses:
            def __init__(inner):inner.calls=[]
            def get(inner,record,key,endpoint):
                inner.calls.append((key,endpoint))
                if key.startswith('reference_'):data=deepcopy(outer.anchor['status'])
                elif key=='boundary':data=deepcopy(outer.old[0])
                elif key=='native_tail_0000':data=[tx('boundary',5),tx('added',4)]
                elif key=='native_tail_0001':data=[]
                else:data=dict(confirmed=True,block_height=parent_height,block_hash='block-'+str(parent_height),block_time=parent_height*100)
                if record_markers:
                    folder=outer.work/'requests/s';folder.mkdir(parents=True,exist_ok=True)
                    body=folder/(key+'.json.gz');body.write_bytes(gzip.compress(json_bytes(data),mtime=0))
                    i=len(inner.calls);when=datetime(2026,11,16,tzinfo=timezone.utc)+timedelta(seconds=i*6)
                    write(folder/(key+'.json'),dict(source_id='s',key=key,provider=PROVIDER,http_status=200,
                        sha256=sha(body),endpoint_sha256=hashlib.sha256(endpoint.encode()).hexdigest(),dispatch_at=when.isoformat(),
                        dispatch_clock_evidence=dict(session_id='test',sequence=i,monotonic_ns=i*6_000_000_000,wall_at=when.isoformat(),enforced_minimum_seconds=5.25)))
                return data
        return Responses()

    def test_absent_parent_is_planned_before_traffic(self):
        legacy_source(self.record,self.work,self.pins)
        self.assertEqual(self.plan['s']['missing_from_saved_prefix'],['same-block-fund'])

    def test_terminal_history_gets_the_planned_same_block_parent_status(self):
        requests=self.responses();e=collect(self.record,requests,self.work,self.q,self.pins)
        self.assertEqual(e['status'],'complete_prior_prefix')
        self.assertTrue(requests.calls[-1][0].startswith('parent_'))
        self.assertEqual(len(requests.calls),6)
        raw=read(self.work/e['raw_file']);self.assertEqual(list(raw['parent_statuses']),['same-block-fund'])
        self.assertEqual(raw['additional_source_transaction_observations'],1)

    def test_parent_missing_from_tail_cannot_be_a_prior_block(self):
        with self.assertRaisesRegex(ValueError,'reference anchor differs'):
            collect(self.record,self.responses(parent_height=9),self.work,self.q,self.pins)
        self.assertFalse(list((self.work/'results').glob('*')))

    def test_bounded_walk_does_not_request_or_infer_parent_closure(self):
        requests=self.responses();self.q['maximum_new_native_pages']=1
        e=collect(self.record,requests,self.work,self.q,self.pins)
        self.assertIsNone(e['features']);self.assertFalse(any(k.startswith('parent_')for k,_ in requests.calls))

    def test_modified_funding_plan_is_rejected_before_requests(self):
        write(self.work/'legacy_funding_plan.json',{})
        requests=self.responses()
        with self.assertRaisesRegex(ValueError,'funding closure changed'):
            collect(self.record,requests,self.work,self.q,self.pins)
        self.assertFalse(requests.calls)

    def test_changed_legacy_endpoint_is_rejected(self):
        self.pins['tail_0000']['endpoint_sha256']='wrong'
        with self.assertRaisesRegex(ValueError,'cursor endpoint differs'):legacy_source(self.record,self.work,self.pins)


class PlannedFundingAuditTests(PlannedFundingTests):
    def setUp(self):
        super().setUp();temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup);self.out=Path(temporary.name)
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'external_cases/cryptobilis_to_coldcard_20261109'))
        write(self.out/'baseline.json',dict(rows=[dict(source_id='s',features=None)]+[
            dict(source_id=f'preserved_{i}',features={'unchanged':i})for i in range(1499)],inputs={}))
        write(self.work/'plan.json',[self.record]);write(self.out/'legacy_reuse_manifest.json',dict(responses=list(self.pins.values())))
        self.q.update(source_ids=['s'],maximum_requests=6,baseline_vectors=1499,
            private_plan_sha256=sha(self.work/'plan.json'),inputs=dict(baseline_view=dict(file='baseline.json',sha256=sha(self.out/'baseline.json'))))
        write(self.out/'protocol.json',self.q)
        e=collect(self.record,self.responses(record_markers=True),self.work,self.q,self.pins)
        self.entry=e
        (self.out/'checkpoint.json.gz').write_bytes(gzip.compress(json_bytes(dict(protocol_sha256=sha(self.out/'protocol.json'),entries={'s':e})),mtime=0))
        self.manifest()
        write(self.out/'run_receipt.json',dict(provider_requests=6,failures=0,operational_locks_released=True,blockstream_provider_requests=0))

    def manifest(self):
        (self.out/'request_manifest.json.gz').write_bytes(gzip.compress(json_bytes([read(p)for p in sorted(self.work.glob('requests/*/*.json'))]),mtime=0))

    def test_independent_replay_verifies_funding_and_recounts_features(self):
        result=audit(self.out,self.work)
        self.assertEqual(result['available_coldcard_vectors'],1500)
        self.assertEqual(result['source_progress'][0]['fresh_funding_statuses'],1)

    def test_parent_status_endpoint_tampering_is_rejected(self):
        path=next((self.work/'requests/s').glob('parent_*.json'));m=read(path);m['endpoint_sha256']='wrong';write(path,m);self.manifest()
        with self.assertRaises(AssertionError):audit(self.out,self.work)

    def test_changed_feature_vector_is_rejected(self):
        self.entry['features']={'made_up':123}
        (self.out/'checkpoint.json.gz').write_bytes(gzip.compress(json_bytes(dict(protocol_sha256=sha(self.out/'protocol.json'),entries={'s':self.entry})),mtime=0))
        with self.assertRaises(AssertionError):audit(self.out,self.work)

    test_absent_parent_is_planned_before_traffic=None
    test_terminal_history_gets_the_planned_same_block_parent_status=None
    test_parent_missing_from_tail_cannot_be_a_prior_block=None
    test_bounded_walk_does_not_request_or_infer_parent_closure=None
    test_modified_funding_plan_is_rejected_before_requests=None
    test_changed_legacy_endpoint_is_rejected=None


if __name__=='__main__':unittest.main()
