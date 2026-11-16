from copy import deepcopy
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
from pathlib import Path
import tempfile
import unittest
import sys

from audit_recorded_mixed_resume import audit
from build_source_registry import json_bytes
from independent_mempool_pilot import PROVIDER
from prepare_frontier_checkpoint import read, sha, write
from recorded_mixed_resume import collect
from test_recorded_priority_campaign import MixedContinuationTests
from test_independent_mempool_bridge import tx


class IndependentMixedAuditTests(MixedContinuationTests):
    def setUp(self):
        super().setUp()
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'external_cases/cryptobilis_to_coldcard_20261109'))
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.out=Path(temporary.name)
        sid=self.record['pilot_id'];old=self.work/'seeds'/sid/'seed_raw.json.gz'
        row=dict(source_id=sid,features=None,precutoff_history_provenance=dict(raw_sha256=sha(old)))
        rows=[row]+[dict(source_id=f'unchanged_{i}',features={'unchanged':i}) for i in range(1499)]
        write(self.out/'baseline.json',dict(rows=rows,inputs={}))
        write(self.out/'parent_resume.json',dict(retained_native_partial_queue=[dict(source_id=sid,
            last_native_cursor_sha256=hashlib.sha256(b'a').hexdigest(),native_pages=50)]))
        write(self.work/'plan.json',[self.record])
        self.q.update(source_ids=[sid],baseline_vectors=1499,maximum_requests=4,
            private_plan_sha256=sha(self.work/'plan.json'),inputs={})
        for name,key in [('baseline.json','baseline_view'),('parent_resume.json','parent_resume')]:
            self.q['inputs'][key]=dict(file=name,sha256=sha(self.out/name))
        write(self.out/'protocol.json',self.q)
        outer=self
        class Responses:
            sequence=0
            def get(inner,record,key,endpoint):
                inner.sequence+=1
                data=deepcopy(outer.old['anchor']['status']) if key.startswith('reference_') else [tx('older',7)] if key=='extension_0000' else []
                folder=outer.work/'requests'/sid;folder.mkdir(parents=True,exist_ok=True)
                body=folder/(key+'.json.gz');body.write_bytes(gzip.compress(json_bytes(data),mtime=0))
                when=datetime(2026,11,16,tzinfo=timezone.utc)+timedelta(seconds=6*inner.sequence)
                write(folder/(key+'.json'),dict(source_id=sid,key=key,provider=PROVIDER,http_status=200,
                    sha256=sha(body),endpoint_sha256=hashlib.sha256(endpoint.encode()).hexdigest(),dispatch_at=when.isoformat(),
                    dispatch_clock_evidence=dict(session_id='test',sequence=inner.sequence,monotonic_ns=6_000_000_000*inner.sequence,
                        wall_at=when.isoformat(),enforced_minimum_seconds=5.25)))
                return data
        e=collect(self.record,Responses(),self.work,self.q,[])
        (self.out/'checkpoint.json.gz').write_bytes(gzip.compress(json_bytes(dict(protocol_sha256=sha(self.out/'protocol.json'),entries={sid:e})),mtime=0))
        self.manifest()
        write(self.out/'run_receipt.json',dict(provider_requests=4,failures=0,operational_locks_released=True,
            blockstream_provider_requests=0,model_fits=0,new_scores=0))

    def manifest(self):
        (self.out/'request_manifest.json.gz').write_bytes(gzip.compress(json_bytes(
            [read(p) for p in sorted((self.work/'requests').glob('*/*.json'))]),mtime=0))

    def test_complete_flow_recounts_features_and_preserves_old_rows(self):
        a=audit(self.out,self.work)
        self.assertEqual((a['available_coldcard_vectors'],a['new_complete_source_ids']),(1500,['s']))
        self.assertEqual(a['fresh_native_source_transaction_observations'],1)

    def test_saved_response_endpoint_mismatch_is_rejected(self):
        path=self.work/'requests/s/extension_0000.json';m=read(path);m['endpoint_sha256']='wrong';write(path,m);self.manifest()
        with self.assertRaises(AssertionError):audit(self.out,self.work)

    def test_parent_native_cursor_mismatch_is_rejected(self):
        path=self.out/'parent_resume.json';v=read(path);v['retained_native_partial_queue'][0]['last_native_cursor_sha256']='wrong';write(path,v)
        self.q['inputs']['parent_resume']['sha256']=sha(path);write(self.out/'protocol.json',self.q)
        cp=read(self.out/'checkpoint.json.gz');cp['protocol_sha256']=sha(self.out/'protocol.json')
        (self.out/'checkpoint.json.gz').write_bytes(gzip.compress(json_bytes(cp),mtime=0))
        with self.assertRaises(AssertionError):audit(self.out,self.work)

    # Base seed/collector regression tests run in their own focused module.
    test_actual_native_cursor_is_preserved_beyond_the_legacy_boundary=None
    test_collection_preserves_union_and_separate_page_counts=None
    test_seed_body_and_cursor_tampering_are_rejected=None
    test_wrong_actual_native_cursor_digest_is_rejected=None
    test_uncrossed_legacy_boundary_is_not_treated_as_native_only=None


if __name__=='__main__':unittest.main()
