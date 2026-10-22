import copy
import json
from pathlib import Path
import unittest
from extend_central_window import check_link, check_selection
from rank_block_recipients import reproduce

ROOT = Path(__file__).resolve().parent


class NeighborTests(unittest.TestCase):
    def setUp(self):
        self.selection=json.loads((ROOT/'neighbor_selection_20261022.json').read_text())
        self.original=json.loads((ROOT/'central_protocol_20261020.json').read_text())

    def test_fixed_symmetric_selection(self):
        check_selection(self.selection,self.original)

    def test_skipped_or_duplicated_neighbor_rejected(self):
        for mutation in ('skip','duplicate'):
            selected=copy.deepcopy(self.selection)
            if mutation=='skip': selected['neighbors'][0]['height']-=1
            else: selected['neighbors'][0]=selected['neighbors'][1]
            with self.assertRaises(ValueError): check_selection(selected,self.original)

    def test_actual_predecessor_and_successor_links_required(self):
        boundary=dict(height=2,hash='middle',prev_block='before')
        check_link(dict(height=1,hash='before'),boundary,'before')
        check_link(dict(height=3,hash='after',prev_block='middle'),boundary,'after')
        for side,block in [('before',dict(height=1,hash='wrong')),
                           ('after',dict(height=3,hash='after',prev_block='wrong'))]:
            with self.assertRaises(ValueError): check_link(block,boundary,side)

    def test_saved_expanded_ranks_reproduce(self):
        result=reproduce(ROOT/'neighbor_results_20261022',ROOT/'neighbor_protocol_20261022.json')
        self.assertTrue(result['reference_rankings_reproduced'])
        self.assertTrue(result['target_scores_recomputed_from_pinned_histories'])


if __name__=='__main__': unittest.main()
