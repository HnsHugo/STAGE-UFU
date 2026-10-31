"""Validate temporal equivalence and fail-closed cursor-tail coverage."""
from copy import deepcopy
import unittest

from build_source_registry import digest
from collect_reference_tail import tail_check
from prepayment_pilot import features, normalize_prefix
from test_source_cohort import records, history
from test_prepayment_pilot import transaction


class ReferenceTailTests(unittest.TestCase):
    def fixture(self):
        record = records(1)[0]
        record.update(payment_txid_sha256=digest(record['payment_txid'].encode()),
                      registry_input_slots=1, reference_input_value_sat=60)
        full = history(record)['transactions']
        anchor = next(t for t in full if t['txid']==record['payment_txid'])
        tail = sorted([t for t in full if t['status']['block_height']<20],
                      key=lambda t:-t['status']['block_height'])
        return record, full, anchor, tail

    def test_exact_full_history_prefix_and_all_features_match(self):
        r, full, anchor, tail = self.fixture()
        same = transaction('e'*64,20,[(r['address'],999)])
        result = tail_check(r,anchor,[same]+tail,True,anchor['status'],{})
        expected = normalize_prefix(r['address'],full,20)
        self.assertEqual(result['prefix'],expected)
        self.assertEqual(result['features'],features(expected,20))
        self.assertFalse(result['audit']['full_history_counter_coverage_verified'])

    def test_unexhausted_tail_does_not_supply_zero_or_partial_features(self):
        r, _, anchor, tail = self.fixture()
        result = tail_check(r,anchor,tail[:1],False,anchor['status'],{})
        self.assertEqual(result['status'],'bounded_incomplete')
        self.assertIsNone(result['features'])

    def test_missing_cursor_cannot_fake_an_empty_prior_prefix(self):
        r, _, anchor, _ = self.fixture()
        with self.assertRaisesRegex(ValueError,'Prior reference funding'):
            tail_check(r,anchor,[],True,anchor['status'],{})

    def test_same_block_funding_may_be_excluded_only_with_its_anchor(self):
        r, _, anchor, _ = self.fixture()
        parent=anchor['vin'][0]['txid']
        result=tail_check(r,anchor,[],True,anchor['status'],{parent:anchor['status']})
        self.assertEqual(result['features']['confirmed_tx_count'],0)
        bad=deepcopy(anchor['status']);bad['block_height']=19
        with self.assertRaisesRegex(ValueError,'Prior reference funding'):
            tail_check(r,anchor,[],True,anchor['status'],{parent:bad})

    def test_reorg_future_and_duplicate_transactions_fail(self):
        r, _, anchor, tail = self.fixture()
        changed=deepcopy(anchor['status']);changed['block_hash']='0'*64
        with self.assertRaisesRegex(ValueError,'anchor changed'):
            tail_check(r,anchor,tail,True,changed,{})
        with self.assertRaisesRegex(ValueError,'reverse-height'):
            tail_check(r,anchor,list(reversed(tail)),True,anchor['status'],{})
        with self.assertRaisesRegex(ValueError,'Repeated'):
            tail_check(r,anchor,tail+tail[-1:],True,anchor['status'],{})


if __name__=='__main__':
    unittest.main()
