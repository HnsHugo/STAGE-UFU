import unittest
from native_twentyfive_campaign import select_ids, PROVIDER


class CampaignSelectionTests(unittest.TestCase):
    def fixture(self,n=28):
        q=[dict(source_id=f's{i:02d}',seed_kind='native',native_pages=32,provider=PROVIDER) for i in reversed(range(n))]
        rows={x['source_id']:{'features':None} for x in q}
        return {'retained_native_partial_queue':q},rows

    def test_exact_five_then_twenty_disjoint_order(self):
        r,v=self.fixture();ids=select_ids(r,v)
        self.assertEqual(ids,[f's{i:02d}' for i in range(25)])
        groups=[ids[i:i+5] for i in range(0,25,5)]
        self.assertEqual([len(x) for x in groups],[5]*5)
        self.assertEqual(len(set(sum(groups,[]))),25)

    def test_excludes_complete_deeper_mixed_and_other_provider(self):
        r,v=self.fixture(32);v['s00']['features']={}
        by_id={x['source_id']:x for x in r['retained_native_partial_queue']}
        by_id['s01']['native_pages']=64;by_id['s02']['seed_kind']='bridge_union';by_id['s03']['provider']='other'
        self.assertEqual(select_ids(r,v),[f's{i:02d}' for i in range(4,29)])

    def test_duplicates_are_rejected(self):
        r,v=self.fixture();r['retained_native_partial_queue'].append(dict(r['retained_native_partial_queue'][0]))
        with self.assertRaises(ValueError):select_ids(r,v)

    def test_exact_count_cannot_silently_shrink(self):
        r,v=self.fixture(24)
        with self.assertRaises(ValueError):select_ids(r,v)


if __name__=='__main__':unittest.main()
