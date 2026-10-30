"""Protect original evidence and unknown labels in the address-level join."""
from copy import deepcopy
import unittest

from prepayment_pilot import FEATURE_NAMES
from combine_comparison_histories import merge,merge_passes


class ComparisonMergeTests(unittest.TestCase):
    def fixture(self):
        selection=[dict(source_id=f'comparison_{i:04d}',address_sha256=str(i)*64,
                        payment_txid_sha256=str(i+3)*64,cutoff_height=10,cutoff_block_hash='b'*64) for i in range(1,4)]
        entries=[]
        for row in selection:
            e={k:row[k] for k in ('address_sha256','payment_txid_sha256','cutoff_height')}
            e.update(status='complete',features=dict.fromkeys(FEATURE_NAMES,0),compromise_label=None,hardware_label=None)
            entries.append(e)
        old={selection[0]['source_id']:entries[0],selection[1]['source_id']:dict(entries[1],status='error',features=None)}
        new={selection[1]['source_id']:entries[1],selection[2]['source_id']:dict(entries[2],status='incomplete',features=None)}
        return selection,old,new,{r['source_id'] for r in selection[1:]}

    def test_original_complete_features_and_both_pass_statuses_are_preserved(self):
        selection,old,new,allowed=self.fixture();before=deepcopy(old)
        rows=merge(selection,old,new,allowed)
        self.assertEqual(old,before)
        self.assertEqual(rows[0]['features'],old['comparison_0001']['features'])
        self.assertEqual(rows[1]['history_provenance']['initial_status'],'error')
        self.assertEqual(rows[1]['history_provenance']['recovery_status'],'complete')
        self.assertIsNone(rows[2]['features'])
        self.assertTrue(all(r['labels']['independently_verified_compromise'] is None for r in rows))
        rows[0]['features']['balance_sat']=999
        self.assertEqual(old,before)

    def test_recovery_cannot_override_successes_or_promote_unknown_labels(self):
        selection,old,new,allowed=self.fixture()
        new['comparison_0001']=deepcopy(old['comparison_0001'])
        with self.assertRaises(ValueError):merge(selection,old,new,allowed|{'comparison_0001'})
        selection,old,new,allowed=self.fixture();new['comparison_0002']['compromise_label']=0
        with self.assertRaises(ValueError):merge(selection,old,new,allowed)

    def test_misassigned_reference_and_unavailable_feature_vectors_are_rejected(self):
        for field,value in [('payment_txid_sha256','x'*64),('cutoff_height',11)]:
            selection,old,new,allowed=self.fixture();new['comparison_0002'][field]=value
            with self.assertRaises(ValueError):merge(selection,old,new,allowed)
        selection,old,new,allowed=self.fixture();new['comparison_0003']['features']={}
        with self.assertRaises(ValueError):merge(selection,old,new,allowed)

    def test_three_pass_history_retains_errors_and_original_complete_features(self):
        selection,old,new,allowed=self.fixture();first=deepcopy(new)
        first['comparison_0002']=dict(new['comparison_0002'],status='error',features=None)
        second={'comparison_0002':new['comparison_0002']}
        before=deepcopy((old,first,second))
        rows=merge_passes(selection,old,[('first',first,allowed),('cooldown',second,{'comparison_0002'})])
        self.assertEqual((old,first,second),before)
        self.assertEqual(rows[0]['features'],old['comparison_0001']['features'])
        self.assertEqual(rows[1]['history_provenance']['chosen_pass'],'cooldown')
        self.assertEqual([p['status'] for p in rows[1]['history_provenance']['recovery_passes']],['error','complete'])
        self.assertEqual(rows[1]['history_provenance']['initial_status'],'error')
        self.assertEqual(rows[2]['history_status'],'incomplete')
        with self.assertRaises(ValueError):
            merge_passes(selection,old,[('first',new,allowed),('cooldown',second,{'comparison_0002'})])


if __name__=='__main__':unittest.main()
