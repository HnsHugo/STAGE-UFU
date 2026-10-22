import unittest
import json
from pathlib import Path
import tempfile
from profile_ranked_recipients import SCORE, describe, select_candidates, run
from test_rank_block_recipients import tx, miner


class ProfileTests(unittest.TestCase):
    def test_boundary_ties_are_all_reviewed(self):
        rows={str(i):{SCORE:s} for i,s in enumerate([9,8,8,1])}
        self.assertEqual(set(select_candidates(rows,2)),{'0','1','2'})
        self.assertEqual(select_candidates({},10),[])

    def test_outputs_count_once_and_self_input_is_not_external(self):
        block=dict(height=1,tx=[miner(),tx('a',[('collector',10),('collector',20)]),
                              tx('b',[('collector',40)],source='collector'),
                              tx('c',[('collector',5)],source=None),
                              tx('d',[('collector',8)],source='other')])
        p=describe('collector',[block])
        self.assertEqual(p['receipt_transactions'],4)
        self.assertEqual(p['external_single_output_transactions'],1)
        self.assertEqual(p['receipt_value_sat']['total'],83)
        self.assertEqual(p['receipts_with_self_input'],1)
        self.assertEqual(p['receipts_with_unknown_input'],1)
        self.assertEqual(p['distinct_qualifying_input_addresses'],1)

    def test_many_input_addresses_do_not_inflate_transaction_score(self):
        funding=tx('a',[('collector',12)])
        funding['inputs']*=3
        p=describe('collector',[dict(height=1,tx=[funding])])
        self.assertEqual(p['external_single_output_transactions'],1)
        self.assertEqual(p['distinct_qualifying_input_addresses'],1)
        self.assertEqual(p['receipts_with_multiple_inputs'],1)

    def test_changed_protocol_rejected_before_reading_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'protocol.json').write_text('{}')
            (root/'summary.json').write_text(json.dumps({'protocol_sha256':'wrong'}))
            with self.assertRaisesRegex(ValueError,'Protocol checksum'):
                run(root/'protocol.json',root/'summary.json',root/'absent-cache')

    def test_future_spending_does_not_enter_profile(self):
        funding=tx('a',[('collector',12)])
        before=describe('collector',[dict(height=1,tx=[funding])])
        funding['out'][0].update(spent=True,spending_outpoints=[dict(tx_index=999)])
        self.assertEqual(before,describe('collector',[dict(height=1,tx=[funding])]))


if __name__=='__main__': unittest.main()
