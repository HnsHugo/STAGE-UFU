import gzip
import hashlib
from pathlib import Path
import tempfile
import unittest

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
from resume_fifty_bridge import seed, collect
from test_independent_mempool_bridge import tx


class FiftyBridgeContracts(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.work=Path(tmp.name)
        (self.work/'raw').mkdir();(self.work/'results').mkdir()
        self.record=dict(pilot_id='comparison_0351',address='source',payment_txid='reference',cutoff_height=100,
            cutoff_block_hash='block-100',registry_input_slots=1,reference_input_value_sat=10,
            address_sha256='address-hash',payment_txid_sha256='reference-hash')
        self.anchor=tx('reference',100);self.anchor['vin']=[dict(txid='fund',vout=0,prevout=dict(scriptpubkey_address='source',value=10))]
        self.old=[tx('fund',90),tx('actual-cursor',80),tx('sorted-last',80)]
        self.raw=dict(anchor=self.anchor,anchor_after=self.anchor['status'],transactions=self.old,pagination_exhausted=False,
            pages_fetched=34,partial_boundary_height=85,legacy_provider_pages=17,independent_provider_pages=17)
        self.spec=dict(raw_file='seed.json.gz',native_cursor='actual-cursor');self.q=dict(maximum_new_native_pages=16,
            native_start_cursor_sha256=hashlib.sha256(b'actual-cursor').hexdigest());self.save()

    def save(self):
        p=self.work/'seed.json.gz';p.write_bytes(gzip.compress(json_bytes(self.raw),mtime=0));self.spec['raw_sha256']=sha(p)
        write(self.work/'bridge_seed.json',self.spec);self.q['private_bridge_seed_sha256']=sha(self.work/'bridge_seed.json')

    def requests(self,pages):
        test=self
        class Fake:
            def __init__(self):self.calls=[]
            def get(self,row,key,endpoint):
                self.calls.append((key,endpoint))
                if key.startswith('reference_'):return test.anchor['status']
                return pages[key]
        return Fake()

    def test_actual_cursor_is_used_and_terminal_closure_preserves_all_seed_transactions(self):
        requests=self.requests({'extension_0000':[tx('new',70)],'extension_0001':[]})
        result=collect(self.record,requests,self.work,self.q,[]);raw=read(self.work/result['raw_file'])
        self.assertTrue(requests.calls[1][1].endswith('/actual-cursor'))
        self.assertEqual(raw['transactions'][:3],self.old);self.assertEqual(result['status'],'complete_prior_prefix')
        self.assertEqual(len(result['features']),14);self.assertEqual(raw['actual_native_last_cursor'],'new')

    def test_changed_seed_body_is_rejected_before_parsing_or_http(self):
        (self.work/'seed.json.gz').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'fingerprint'):seed(self.record,self.work,self.q)

    def test_legacy_boundary_must_be_strictly_above_the_native_frontier(self):
        self.raw['partial_boundary_height']=80;self.save()
        with self.assertRaisesRegex(ValueError,'separate'):seed(self.record,self.work,self.q)

    def test_sixteen_nonempty_extension_pages_keep_null_features_and_separate_page_counts(self):
        requests=self.requests({f'extension_{i:04d}':[tx(f'new-{i}',79-i)] for i in range(16)})
        result=collect(self.record,requests,self.work,self.q,[]);raw=read(self.work/result['raw_file'])
        self.assertEqual((result['status'],result['features'],result['prefix']),('bounded_incomplete',None,None))
        self.assertEqual(raw['transactions'][:3],self.old)
        self.assertEqual((raw['pages_fetched'],raw['independent_provider_pages'],raw['legacy_provider_pages']),(50,33,17))


if __name__=='__main__':unittest.main()
