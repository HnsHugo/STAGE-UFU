"""Prove that a saved 32-page prefix can continue without replay or false completion."""
import gzip
import hashlib
from pathlib import Path
import sys
import tempfile
from threading import Event
import unittest
from unittest.mock import Mock

BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
from build_source_registry import json_bytes
from collect_comparison_coverage import Pages
from collect_reference_tail import collect_one
import test_reference_tail as fixtures
from test_prepayment_pilot import transaction


class DeeperResumeTests(unittest.TestCase):
    def run_case(self,exhausted):
        record,_,anchor,tail=fixtures.ReferenceTailTests().fixture()
        lowest=tail[-1]['status']['block_height']
        batches=[tail]+[[transaction(hashlib.sha256(('extra-%d'%i).encode()).hexdigest(),lowest,[(record['address'],1)])] for i in range(1,64)]
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)
            for name in ['raw','results']:(work/name).mkdir()
            folder=work/'requests'/record['pilot_id'];folder.mkdir(parents=True)
            cursor=record['payment_txid']
            for key,value,endpoint in [('reference',anchor,'/tx/'+record['payment_txid'])]+[
                    ('tail_%04d'%i,batches[i],None) for i in range(32)]:
                if endpoint is None:endpoint='/address/'+record['address']+'/txs/chain/'+cursor
                raw=gzip.compress(json_bytes(value),mtime=0)
                (folder/(key+'.json.gz')).write_bytes(raw)
                (folder/(key+'.json')).write_bytes(json_bytes(dict(source_id=record['pilot_id'],key=key,http_status=200,
                    sha256=hashlib.sha256(raw).hexdigest(),endpoint_sha256=hashlib.sha256(endpoint.encode()).hexdigest(),offline_reused=True)))
                if key.startswith('tail_'):cursor=value[-1]['txid']
            responses=([[]] if exhausted else batches[32:64])+[anchor['status']]
            http=Mock();http.get_json.side_effect=responses
            result=collect_one(record,Pages(work,http,Event()),work,64)
            self.assertTrue(http.get_json.call_args_list[0].args[0].endswith('/txs/chain/'+cursor))
            self.assertEqual(http.get_json.call_count,2 if exhausted else 33)
            self.assertEqual(result['pages_fetched'],33 if exhausted else 64)
            if exhausted:self.assertEqual(result['status'],'complete_prior_prefix')
            else:
                self.assertEqual(result['status'],'bounded_incomplete')
                self.assertIsNone(result['features']);self.assertIsNone(result['prefix'])

    def test_saved_32_pages_continue_to_empty_page_without_old_http(self):self.run_case(True)
    def test_64_nonempty_pages_still_have_no_manufactured_features(self):self.run_case(False)


if __name__=='__main__':unittest.main()
