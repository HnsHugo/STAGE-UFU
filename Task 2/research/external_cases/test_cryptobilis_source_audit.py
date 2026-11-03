"""Composition must preserve completed rows, labels and history semantics."""
from copy import deepcopy
import unittest

from audit_cryptobilis_sources import compose, fixed


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.row=dict(source_id='source',address_sha256='a',reference_txid_sha256='t',
                      cutoff_height=10,cutoff_block_hash='b',labels={'compromise':None,'device':None},
                      full_history_status='not_collected',cryptobilis_reference_source_membership=1,
                      precutoff_history_status='not_completed',prior_prefix_status='not_completed',features=None)
        self.entry=dict(address_sha256='a',payment_txid_sha256='t',cutoff_height=10,
                        cutoff_block_hash='b',status='complete_prior_prefix',prefix=[],
                        features=fixed.features([],10),raw_sha256='raw')

    def test_success_keeps_unknown_labels_and_unverified_full_history(self):
        baseline=dict(schema_version=2,rows=[deepcopy(self.row)])
        result=compose(baseline,{'source':self.entry},'new')
        self.assertEqual(result['rows'][0]['labels'],self.row['labels'])
        self.assertEqual(result['rows'][0]['full_history_status'],'not_collected')
        self.assertIsNone(baseline['rows'][0]['features'])

    def test_finished_source_cannot_be_selected_again(self):
        self.row.update(features=self.entry['features'],precutoff_history_status='complete_prior_prefix')
        with self.assertRaisesRegex(ValueError,'Finished'):
            compose(dict(schema_version=2,rows=[self.row]),{'source':self.entry},'new')

    def test_incomplete_cannot_supply_vector(self):
        self.entry['status']='bounded_incomplete'
        with self.assertRaisesRegex(ValueError,'Incomplete'):
            compose(dict(schema_version=2,rows=[self.row]),{'source':self.entry},'new')

    def test_changed_cutoff_rejected(self):
        self.entry['cutoff_height']=11
        with self.assertRaisesRegex(ValueError,'cutoff'):
            compose(dict(schema_version=2,rows=[self.row]),{'source':self.entry},'new')


if __name__ == '__main__':
    unittest.main()
