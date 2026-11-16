from copy import deepcopy
import gzip
import hashlib
from pathlib import Path
import tempfile
import unittest

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
from recorded_mixed_resume import seed, collect
from recorded_priority_campaign import build_units
from test_independent_mempool_bridge import tx


class PrioritySelectionTests(unittest.TestCase):
    def test_exact_selection_is_counter_ordered_with_uniform_small_units(self):
        candidates = [dict(source_id=f's{i:02d}', historical_full_current_counter=100-i,
            kind='native' if i % 2 else 'legacy_bridge', previous_bound=32 if i % 2 == 0 else 278)
            for i in range(25)]
        chosen, units = build_units(candidates)
        self.assertEqual([c['source_id'] for c in chosen], [f's{i:02d}' for i in range(24,4,-1)])
        flattened = sum((u['source_ids'] for u in units), [])
        self.assertEqual(len(flattened), len(set(flattened)))
        self.assertEqual(set(flattened), {c['source_id'] for c in chosen})
        self.assertTrue(all(1 <= len(u['source_ids']) <= 3 for u in units))
        by_id = {c['source_id']:c for c in candidates}
        self.assertTrue(all(all((by_id[s]['kind'],by_id[s]['previous_bound']) ==
            (u['kind'],u['previous_bound']) for s in u['source_ids']) for u in units))

    def test_duplicate_and_short_selections_are_rejected(self):
        item = dict(source_id='s', historical_full_current_counter=1, kind='native', previous_bound=1)
        with self.assertRaises(AssertionError): build_units([item]*20)
        with self.assertRaises(AssertionError): build_units([item])


class MixedContinuationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        for name in ['raw','results','seeds']:
            (self.work/name).mkdir()
        self.record = dict(pilot_id='s',address='source',payment_txid='reference',cutoff_height=10,
            cutoff_block_hash='block-10',registry_input_slots=1,reference_input_value_sat=10,
            address_sha256='address-hash',payment_txid_sha256='reference-hash')
        anchor=tx('reference',10)
        anchor['vin']=[dict(txid='fund',vout=0,prevout=dict(scriptpubkey_address='source',value=10))]
        # A sorted union ends in z, whereas the saved native walk ended in a.
        self.old=dict(anchor=anchor,transactions=[tx('fund',9),tx('a',8),tx('z',8)],
            pagination_exhausted=False,pages_fetched=82,independent_provider_pages=50,
            legacy_provider_pages=32,partial_boundary_height=9)
        folder=self.work/'seeds'/'s';folder.mkdir()
        (folder/'seed_raw.json.gz').write_bytes(gzip.compress(json_bytes(self.old),mtime=0))
        write(folder/'bridge_seed.json',dict(raw_file='seed_raw.json.gz',raw_sha256=sha(folder/'seed_raw.json.gz'),native_cursor='a'))
        self.index={'s':dict(spec_sha256=sha(folder/'bridge_seed.json'),native_cursor_sha256=hashlib.sha256(b'a').hexdigest())}
        write(self.work/'bridge_seed_index.json',self.index)
        self.q=dict(private_bridge_seed_index_sha256=sha(self.work/'bridge_seed_index.json'),maximum_new_native_pages=2)

    def test_actual_native_cursor_is_preserved_beyond_the_legacy_boundary(self):
        spec,old,values,seen,height=seed(self.record,self.work,self.q)
        self.assertEqual((spec['native_cursor'],values[-1]['txid'],height),('a','z',8))

    def test_collection_preserves_union_and_separate_page_counts(self):
        calls=[]
        class Responses:
            def get(inner,record,key,endpoint):
                calls.append((key,endpoint))
                if key.startswith('reference_'):return deepcopy(self.old['anchor']['status'])
                return [tx('older',7)] if key=='extension_0000' else []
        e=collect(self.record,Responses(),self.work,self.q,[])
        raw=read(self.work/e['raw_file'])
        self.assertEqual(calls[1][1],'/address/source/txs/chain/a')
        self.assertEqual(raw['transactions'][:3],self.old['transactions'])
        self.assertEqual((raw['independent_provider_pages'],raw['legacy_provider_pages'],raw['pages_fetched']),(52,32,84))
        self.assertEqual(e['status'],'complete_prior_prefix')

    def test_seed_body_and_cursor_tampering_are_rejected(self):
        path=self.work/'seeds'/'s'/'seed_raw.json.gz';path.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'raw fingerprint'):seed(self.record,self.work,self.q)

    def test_wrong_actual_native_cursor_digest_is_rejected(self):
        self.index['s']['native_cursor_sha256']='wrong';write(self.work/'bridge_seed_index.json',self.index)
        self.q['private_bridge_seed_index_sha256']=sha(self.work/'bridge_seed_index.json')
        with self.assertRaisesRegex(ValueError,'Actual native cursor'):seed(self.record,self.work,self.q)

    def test_uncrossed_legacy_boundary_is_not_treated_as_native_only(self):
        self.old['partial_boundary_height']=8
        folder=self.work/'seeds'/'s'
        (folder/'seed_raw.json.gz').write_bytes(gzip.compress(json_bytes(self.old),mtime=0))
        spec=read(folder/'bridge_seed.json');spec['raw_sha256']=sha(folder/'seed_raw.json.gz');write(folder/'bridge_seed.json',spec)
        self.index['s']['spec_sha256']=sha(folder/'bridge_seed.json');write(self.work/'bridge_seed_index.json',self.index)
        self.q['private_bridge_seed_index_sha256']=sha(self.work/'bridge_seed_index.json')
        with self.assertRaisesRegex(ValueError,'separate the legacy boundary'):seed(self.record,self.work,self.q)


if __name__=='__main__':unittest.main()
