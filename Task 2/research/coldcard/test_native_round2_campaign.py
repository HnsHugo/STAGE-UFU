import unittest
from native_round2_campaign import select_ids, build_units, PROVIDER


class RemainingNativeTests(unittest.TestCase):
    def fixture(self):
        queue=[]
        for bound,n in [(80,4),(48,3),(64,17)]:
            queue += [dict(source_id=f'{bound}_{i:02d}',native_pages=bound,seed_kind='native',provider=PROVIDER) for i in reversed(range(n))]
        return {'retained_native_partial_queue':queue},{x['source_id']:{'features':None} for x in queue}

    def test_all_frontiers_selected_in_bound_then_id_order(self):
        resume,rows=self.fixture();ids=select_ids(resume,rows);units=build_units(resume,ids)
        self.assertEqual(len(ids),24)
        self.assertEqual([len(u) for u in units],[3,5,5,5,2,4])
        self.assertEqual(sum(units,[]),ids)
        bounds={x['source_id']:x['native_pages'] for x in resume['retained_native_partial_queue']}
        self.assertTrue(all(len({bounds[s] for s in u})==1 for u in units))
        self.assertEqual([bounds[u[0]] for u in units],[48,64,64,64,64,80])

    def test_completed_mixed_or_other_provider_sources_excluded(self):
        resume,rows=self.fixture();items={x['source_id']:x for x in resume['retained_native_partial_queue']}
        rows['48_00']['features']={};items['64_00']['seed_kind']='bridge_union';items['80_00']['provider']='other'
        ids=select_ids(resume,rows)
        self.assertEqual(len(ids),21)
        self.assertTrue({'48_00','64_00','80_00'}.isdisjoint(ids))

    def test_duplicate_frontier_rejected(self):
        resume,rows=self.fixture();resume['retained_native_partial_queue'].append(dict(resume['retained_native_partial_queue'][0]))
        with self.assertRaises(ValueError):select_ids(resume,rows)

    def test_optional_exact_count_cannot_shrink(self):
        resume,rows=self.fixture()
        with self.assertRaises(ValueError):select_ids(resume,rows,25)
        self.assertEqual(len(select_ids(resume,rows,3)),3)


if __name__=='__main__':unittest.main()
