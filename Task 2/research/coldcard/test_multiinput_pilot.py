"""Check multi-input selection and reuse of the fixed temporal extractor."""
import copy
import unittest

from multiinput_pilot import choose, prefix_for
from prepayment_pilot import features
from test_prepayment_pilot import history_transactions


class MultiInputTests(unittest.TestCase):
    def test_only_candidate_multi_input_sources_are_eligible_and_order_independent(self):
        rows=[dict(address="one",scopes=["candidate_window"],spent_previous_output_count=1),
              dict(address="two",scopes=["candidate_window"],spent_previous_output_count=2),
              dict(address="many",scopes=["candidate_window"],spent_previous_output_count=9),
              dict(address="later",scopes=["outside_candidate_window"],spent_previous_output_count=20)]
        protocol=dict(population_scope="candidate_window",min_payment_inputs=2,sample_size=2,sampling_prefix="fixed:42:")
        selected,population=choose(rows,protocol)
        self.assertEqual(population,2)
        self.assertEqual({r["address"] for r in selected},{"two","many"})
        self.assertEqual((selected,population),choose(list(reversed(rows)),protocol))

    def test_insufficient_population_is_not_filled_with_single_input_addresses(self):
        row=dict(address="single",scopes=["candidate_window"],spent_previous_output_count=1)
        protocol=dict(population_scope="candidate_window",min_payment_inputs=2,sample_size=1,sampling_prefix="fixed:42:")
        with self.assertRaisesRegex(ValueError,"Insufficient eligible"):
            choose([row],protocol)

    def fixture(self):
        record=dict(address="source",payment_txid="c"*64,cutoff_height=20,cutoff_block_hash="f"*64)
        counters=dict(tx_count=4,funded_txo_count=3,funded_txo_sum=1100,spent_txo_count=2,spent_txo_sum=100)
        history=dict(address="source",transactions=history_transactions(),audit=dict(pagination_exhausted=True),
                     before=dict(address="source",chain_stats=counters),after=dict(address="source",chain_stats=copy.deepcopy(counters)))
        return record,history

    def test_complete_history_reuses_strict_prior_block_features(self):
        record,history=self.fixture()
        prefix=prefix_for(record,history)
        self.assertEqual({t["height"] for t in prefix},{10,15})
        self.assertEqual(features(prefix,20)["balance_sat"],60)
        history["transactions"][-1]["status"]["block_time"]=0
        self.assertEqual(prefix,prefix_for(record,history))

    def test_incomplete_history_is_unavailable_not_an_empty_history(self):
        record,history=self.fixture()
        history["audit"]["pagination_exhausted"]=False
        self.assertIsNone(prefix_for(record,history))

    def test_mismatched_reference_payment_anchor_is_rejected(self):
        record,history=self.fixture()
        record["cutoff_height"]=21
        with self.assertRaisesRegex(ValueError,"cutoff anchor"):
            prefix_for(record,history)


if __name__=="__main__":unittest.main()
