import gzip
import hashlib
from pathlib import Path
import tempfile
import unittest

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import sha,write
from independent_mempool_pilot import PROVIDER
from independent_mempool_resume import cached_prefix
from test_independent_mempool_bridge import tx


class NativeResumeContracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.work=Path(self.temp.name);self.folder=self.work/'requests'/'source_1';self.folder.mkdir(parents=True)
        self.record=dict(pilot_id='source_1',address='source',payment_txid='reference',cutoff_height=10,
            cutoff_block_hash='block-10',registry_input_slots=1,reference_input_value_sat=10)
        anchor=tx('reference',10);anchor['vin']=[dict(txid='fund',vout=0,prevout=dict(scriptpubkey_address='source',value=10))]
        self.pins=[self.response('reference','/tx/reference',anchor),
            self.response('tail_0000','/address/source/txs/chain/reference',[tx('fund',8),tx('boundary',8)])]

    def response(self,key,endpoint,data):
        p=self.folder/(key+'.json.gz');p.write_bytes(gzip.compress(json_bytes(data),mtime=0))
        m=dict(key=key,source_id='source_1',http_status=200,offline_reused=True,provider=PROVIDER,
            sha256=sha(p),endpoint_sha256=hashlib.sha256(endpoint.encode()).hexdigest())
        write(self.folder/(key+'.json'),m);return m

    def test_reuse_returns_exact_native_cursor_and_all_old_transactions(self):
        _,pages,cursor,seen,height,terminal=cached_prefix(self.record,self.work,self.pins)
        self.assertEqual((len(pages),cursor,height,terminal),(1,'boundary',8,False))
        self.assertEqual(seen,{'reference','fund','boundary'})

    def test_changed_cached_body_is_rejected(self):
        (self.folder/'tail_0000.json.gz').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'body differs'):cached_prefix(self.record,self.work,self.pins)

    def test_unknown_consumed_intent_is_never_a_reusable_page(self):
        write(self.folder/'tail_0000.json',dict(source_id='source_1',key='tail_0000',offline_reused=True))
        with self.assertRaisesRegex(ValueError,'consumed original intent'):cached_prefix(self.record,self.work,self.pins)

    def test_cursor_endpoint_mismatch_is_rejected(self):
        self.pins[1]['endpoint_sha256']='wrong'
        with self.assertRaisesRegex(ValueError,'endpoint differs'):cached_prefix(self.record,self.work,self.pins)

    def test_wrong_provider_is_not_accepted_as_native_reuse(self):
        p=self.folder/'tail_0000.json';m=__import__('json').loads(p.read_text());m['provider']='https://blockstream.info/api';write(p,m)
        with self.assertRaisesRegex(ValueError,'endpoint differs'):cached_prefix(self.record,self.work,self.pins)

    def test_page_after_terminal_is_rejected(self):
        self.pins[1]=self.response('tail_0000','/address/source/txs/chain/reference',[])
        self.pins.append(self.response('tail_0001','/address/source/txs/chain/reference',[tx('later',8)]))
        with self.assertRaisesRegex(ValueError,'follows terminal'):cached_prefix(self.record,self.work,self.pins)

    def test_fresh_source_starts_from_frozen_reference_without_fake_reuse(self):
        anchor,pages,cursor,seen,height,terminal=cached_prefix(self.record,self.work,[])
        self.assertEqual((anchor,pages,cursor,seen,height,terminal),(None,[],'reference',{'reference'},10,False))


if __name__=='__main__':unittest.main()
