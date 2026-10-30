"""Exercise source-only selection and preserve unknown compromise labels."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from build_source_registry import digest
from source_comparison_design import audit, census, check_case_anchors, choose, load_design, replay


ROOT=Path(__file__).resolve().parent
PROTOCOL=ROOT/'source_comparison_design_20261030/protocol.json'


def transaction(txid, addresses, recipient='output_only'):
    inputs=[dict(prev_out=dict(addr=a,value=10)) for a in addresses]
    return dict(hash=txid,inputs=inputs,out=[dict(n=0,addr=recipient,value=9)],
                vin_sz=len(inputs),vout_sz=1)


def block(height, transactions):
    cb=dict(hash='coinbase'+str(height),inputs=[dict(prev_out=dict(tx_index=0,n=4294967295))],
            out=[dict(n=0,addr='miner',value=50)],vin_sz=1,vout_sz=1)
    return dict(height=height,hash='block'+str(height),time=height,main_chain=True,
                n_tx=1+len(transactions),tx=[cb]+transactions)


def anchors(blocks):
    return [{k:b[k] for k in ('height','hash','time')} for b in blocks]


class SourceComparisonTests(unittest.TestCase):
    def test_census_uses_inputs_and_omits_coinbase_outputs_and_unresolved_addresses(self):
        blocks=[block(10,[transaction('tx1',['source',None])])]
        first,_,stats=census(blocks,anchors(blocks))
        self.assertEqual(set(first),{'source'})
        self.assertEqual(stats[0]['unresolved_address_input_observations'],1)
        self.assertNotIn('output_only',first)
        self.assertNotIn('miner',first)

    def test_repeated_source_gets_first_height_and_lexical_reference(self):
        blocks=[block(10,[transaction('z',['a']),transaction('b',['a'])]),
                block(11,[transaction('a',['a'])])]
        first,_,_=census(list(reversed(blocks)),anchors(blocks))
        self.assertEqual((first['a']['cutoff_height'],first['a']['reference_txid']),(10,'b'))

    def test_missing_repeated_bad_anchor_and_truncated_blocks_are_rejected(self):
        blocks=[block(10,[transaction('a',['source'])]),block(11,[])]
        for changed in [blocks[:1],[blocks[0],blocks[0]]]:
            with self.assertRaises(ValueError):census(changed,anchors(blocks))
        for field,value in [('hash','wrong'),('n_tx',123)]:
            changed=deepcopy(blocks);changed[0][field]=value
            with self.assertRaises(ValueError):census(changed,anchors(blocks))

    def test_amountless_prevout_fails_instead_of_inventing_sources(self):
        blocks=[block(10,[transaction('a',['source'])])];del blocks[0]['tx'][1]['inputs'][0]['prev_out']['value']
        with self.assertRaises(ValueError):census(blocks,anchors(blocks))

    def test_selector_excludes_all_known_related_addresses_and_is_order_invariant(self):
        blocks=[block(10,[transaction('a',['case','later_case','collector','x','y','z'])])]
        first,_,_=census(blocks,anchors(blocks));excluded={'case','later_case','collector'}
        quota=[dict(height=10,comparison_quota=2)]
        chosen,stats=choose(first,excluded,quota,'seed:42:')
        again,_=choose(dict(reversed(list(first.items()))),excluded,quota,'seed:42:')
        self.assertEqual(chosen,again)
        self.assertTrue(all(r['address'] not in excluded for r in chosen))
        self.assertEqual([r['address'] for r in chosen],sorted(['x','y','z'],key=lambda a:digest(('seed:42:'+a).encode()))[:2])
        self.assertEqual(stats[0]['eligible_sources'],3)

    def test_short_strata_are_not_filled_from_other_blocks(self):
        first={a:dict(address=a,cutoff_height=h) for a,h in [('x',10),('y',11),('z',11)]}
        chosen,stats=choose(first,set(),[dict(height=10,comparison_quota=3),dict(height=11,comparison_quota=1)],'seed:')
        self.assertEqual(len(chosen),2)
        self.assertEqual([s['shortfall'] for s in stats],[2,0])

    def test_case_input_anchor_values_cannot_be_substituted_by_recipient_matches(self):
        tx=transaction('payment',['case'])
        records=[dict(pilot_id='cohort_1',address='case',payment_txid='payment',cutoff_height=10)]
        rows=[dict(source_id='cohort_1',event_evidence=dict(observed_input_count=1,observed_input_value_sat=10))]
        check_case_anchors(records,rows,{'payment':(10,tx)})
        for changed in [{},{'payment':(11,tx)},{'payment':(10,transaction('payment',['elsewhere'],recipient='case'))}]:
            with self.assertRaises(ValueError):check_case_anchors(records,rows,changed)

    def test_design_reconciles_real_case_and_does_not_claim_sample_or_model(self):
        with tempfile.TemporaryDirectory() as folder:
            result=audit(PROTOCOL,Path(folder))
        self.assertTrue(result['design_valid'])
        self.assertEqual(sum(q['comparison_quota'] for q in result['case_sources_and_comparison_quotas']),1000)
        self.assertEqual(result['excluded_known_related_addresses'],506)
        self.assertIsNone(result['comparison_population_size'])
        self.assertFalse(result['comparisons_selected'])
        self.assertFalse(result['model_fitted'])
        self.assertEqual(result['available_block_files'],0)

    def test_wrong_input_pin_or_quota_fails_preflight(self):
        protocol=json.loads(PROTOCOL.read_bytes())
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path=Path(folder)/'protocol.json'
            changed=deepcopy(protocol);changed['inputs']['source_view']['sha256']='0'*64
            path.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):load_design(path)
            changed=deepcopy(protocol);changed['comparison_selection']['quotas'][0]['comparison_quota']+=1
            path.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):load_design(path)

    def test_public_census_replays_selection_without_raw_cache(self):
        out=ROOT/'source_comparison_selection_20261030'
        actual=replay(PROTOCOL,out/'census.json.gz')
        self.assertEqual(actual,json.loads((out/'selection.json').read_bytes()))
        self.assertEqual(len(actual['rows']),1000)
        self.assertTrue(all(r['features'] is None and r['compromise_label'] is None
                            and r['hardware_label'] is None for r in actual['rows']))

    def test_redacted_exclusion_tampering_is_rejected(self):
        import gzip
        out=ROOT/'source_comparison_selection_20261030'
        normalized=json.loads(gzip.decompress((out/'census.json.gz').read_bytes()))
        normalized['sources'][0]['excluded_known_related']=not normalized['sources'][0]['excluded_known_related']
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'census.json.gz';path.write_bytes(gzip.compress(json.dumps(normalized).encode()))
            with self.assertRaises(ValueError):replay(PROTOCOL,path)


if __name__=='__main__':unittest.main()
