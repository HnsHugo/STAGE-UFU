"""A closure claim must reject gaps, label promotion and partial vectors."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from audit_cryptobilis_acquisition_closure import validate_view, check_cached_assembly, fixed


class ClosureGateTests(unittest.TestCase):
    def setUp(self):
        self.original=dict(source_id='case',address_sha256='address',reference_txid_sha256='reference',
                           cutoff_height=10,cutoff_block_hash='block',labels={'compromise':None,'device':None},
                           case_relation='graph_candidate',cryptobilis_reference_source_membership=1,
                           prior_prefix_status='not_collected_in_this_unit',features=None)
        row=deepcopy(self.original)
        row.update(precutoff_history_status='complete_prior_prefix',prior_prefix_status='complete_prior_prefix',
                   full_history_status='not_collected_for_this_source',features=fixed.features([],10))
        self.view=dict(schema_version=2,rows=[row]);self.selected=dict(rows=[self.original])

    def test_complete_prefix_accepts_unknown_labels(self):
        self.assertEqual(set(validate_view(self.view,self.selected)),{'case'})

    def test_bounded_prefix_with_no_vector_is_final_outcome(self):
        self.view['rows'][0].update(precutoff_history_status='bounded_incomplete',prior_prefix_status='bounded_incomplete',features=None)
        self.assertIsNone(validate_view(self.view,self.selected)['case']['features'])

    def test_unattempted_row_prevents_closure(self):
        self.view['rows'][0].update(precutoff_history_status='not_completed',prior_prefix_status='not_completed',features=None)
        with self.assertRaisesRegex(ValueError,'remains'):validate_view(self.view,self.selected)

    def test_nonexhausted_prefix_cannot_supply_vector(self):
        self.view['rows'][0].update(precutoff_history_status='bounded_incomplete',prior_prefix_status='bounded_incomplete')
        with self.assertRaisesRegex(ValueError,'supplies'):validate_view(self.view,self.selected)

    def test_reference_change_is_rejected(self):
        self.view['rows'][0]['reference_txid_sha256']='other'
        with self.assertRaisesRegex(ValueError,'changed'):validate_view(self.view,self.selected)

    def test_verified_label_cannot_be_manufactured(self):
        self.view['rows'][0]['labels']['device']=True
        with self.assertRaisesRegex(ValueError,'changed'):validate_view(self.view,self.selected)

    def test_prefix_never_promotes_full_current_history(self):
        self.view['rows'][0]['full_history_status']='complete'
        with self.assertRaisesRegex(ValueError,'promoted'):validate_view(self.view,self.selected)

    def test_duplicate_record_is_rejected(self):
        self.view['rows'].append(deepcopy(self.view['rows'][0]))
        with self.assertRaisesRegex(ValueError,'repeated'):validate_view(self.view,self.selected)


class CachedAssemblyTests(unittest.TestCase):
    def check_fixture(self, changed=False):
        with TemporaryDirectory() as directory:
            work=Path(directory);folder=work/'requests/source';folder.mkdir(parents=True)
            anchor={'txid':'reference'};after={'confirmed':True};transactions=[{'txid':'prior'}]
            bodies={'reference':anchor,'reference_after':after,'tail_0000':transactions,'tail_0001':[]}
            for key,value in bodies.items():
                (folder/(key+'.json.gz')).write_bytes(gzip.compress(json.dumps(value).encode()))
            data=dict(anchor=anchor,anchor_after=after,transactions=deepcopy(transactions),
                      parent_statuses={},pages_fetched=2,pagination_exhausted=True)
            if changed:data['transactions'][0]['txid']='omitted-or-replaced'
            check_cached_assembly({'pilot_id':'source'},data,work)

    def test_raw_assembly_matches_saved_pages(self):
        self.check_fixture()

    def test_replaced_transaction_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'differs'):self.check_fixture(changed=True)


if __name__=='__main__':
    unittest.main()
