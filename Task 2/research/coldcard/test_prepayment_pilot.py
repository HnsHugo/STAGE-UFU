"""Test temporal isolation, balance reconstruction and incomplete-data handling."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from build_source_registry import digest, json_bytes
from prepayment_pilot import analyze, features, normalize_prefix


def transaction(tid, height, outputs, inputs=(), fee=1):
    return dict(txid=tid, status=dict(confirmed=True, block_height=height,
                                     block_hash="f"*64, block_time=height),
                vout=[dict(scriptpubkey_address=a, value=v, spent=True) for a,v in outputs],
                vin=list(inputs), fee=fee, weight=400)


def inp(tid,index,value):
    return dict(txid=tid,vout=index,prevout=dict(scriptpubkey_address="source",value=value))


def history_transactions():
    return [transaction("a"*64,10,[("source",60),("source",40)]),
            transaction("b"*64,15,[("other",39)],[inp("a"*64,1,40)]),
            transaction("c"*64,20,[("collector",59)],[inp("a"*64,0,60)]),
            transaction("d"*64,21,[("source",1000)])]


class PrepaymentTests(unittest.TestCase):
    def test_balance_counts_ages_and_fee_units(self):
        result=features(normalize_prefix("source",history_transactions(),20),20)
        self.assertEqual(result["confirmed_tx_count"],2)
        self.assertEqual(result["received_sat"],100)
        self.assertEqual(result["spent_sat"],40)
        self.assertEqual(result["balance_sat"],60)
        self.assertEqual(result["unspent_output_count"],1)
        self.assertEqual(result["activity_span_blocks"],5)
        self.assertEqual(result["blocks_since_last_activity"],5)
        self.assertEqual(result["median_spending_tx_fee_rate_sat_vb"],0.01)

    def test_payment_block_and_future_changes_do_not_change_features(self):
        txs=history_transactions()
        expected=normalize_prefix("source",txs,20)
        txs[2]["fee"]=10**9
        txs[2]["vout"][0]["value"]=10**12
        txs[3]["vout"][0]["value"]=10**15
        txs.append(transaction("e"*64,20,[("source",999)]))
        self.assertEqual(expected,normalize_prefix("source",txs,20))

    def test_height_cutoff_not_nonmonotone_block_time(self):
        txs=history_transactions()
        txs[0]["status"]["block_time"]=10**10
        txs[3]["status"]["block_time"]=0
        prefix=normalize_prefix("source",txs,20)
        self.assertEqual({t["height"] for t in prefix},{10,15})

    def test_future_spent_flags_and_incoming_fees_are_not_features(self):
        tx=history_transactions()[0]
        tx["fee"]=999999
        first=features(normalize_prefix("source",[tx],20),20)
        tx["vout"][0]["spent"]=False
        tx["vout"][1]["spent"]=False
        self.assertEqual(first,features(normalize_prefix("source",[tx],20),20))
        self.assertIsNone(first["median_spending_tx_fee_rate_sat_vb"])

    def test_outpoint_value_or_absent_receipt_rejected(self):
        prefix=normalize_prefix("source",history_transactions(),20)
        prefix[1]["spent"][0]["value_sat"]=41
        with self.assertRaisesRegex(ValueError,"Historical spent output"):
            features(prefix,20)
        prefix=normalize_prefix("source",history_transactions(),20)
        with self.assertRaisesRegex(ValueError,"Historical spent output"):
            features(prefix[1:],20)

    def test_duplicate_and_future_prefix_evidence_rejected(self):
        prefix=normalize_prefix("source",history_transactions(),20)
        with self.assertRaisesRegex(ValueError,"Duplicate prefix transaction"):
            features(prefix+[copy.deepcopy(prefix[0])],20)
        prefix[0]["height"]=20
        with self.assertRaisesRegex(ValueError,"future evidence"):
            features(prefix,20)

    def test_empty_complete_prefix_has_zero_counts_but_unknown_ages(self):
        result=features([],20)
        self.assertEqual(result["balance_sat"],0)
        self.assertEqual(result["confirmed_tx_count"],0)
        self.assertIsNone(result["blocks_since_first_activity"])
        self.assertIsNone(result["median_spending_tx_fee_rate_sat_vb"])

    def test_transaction_read_order_does_not_change_prefix_or_features(self):
        txs=history_transactions()
        self.assertEqual(normalize_prefix("source",txs,20),normalize_prefix("source",list(reversed(txs)),20))

    def test_incomplete_snapshot_does_not_become_zero_features_or_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);protocol_path=root/"protocol.json";protocol_path.write_bytes(b"{}")
            selected=[dict(pilot_id="source_01",address="source",cutoff_height=20,
                           cutoff_block_hash="f"*64,payment_txid="c"*64,registry_input_slots=1)]
            counters=dict(tx_count=4,funded_txo_count=3,funded_txo_sum=1100,
                          spent_txo_count=2,spent_txo_sum=100)
            data=dict(address="source",transactions=history_transactions(),
                      before=dict(address="source",chain_stats=counters),
                      after=dict(address="source",chain_stats=counters),
                      audit=dict(pagination_exhausted=False))
            raw=gzip.compress(json_bytes(data),mtime=0);(root/"history.gz").write_bytes(raw)
            manifest=dict(protocol_sha256=digest(b"{}"),selection_sha256=digest(json_bytes(selected)),
                          results=[dict(pilot_id="source_01",file="history.gz",sha256=digest(raw))])
            (root/"collection_manifest.json").write_bytes(json_bytes(manifest))
            with patch("prepayment_pilot.load_protocol",return_value=({"case_id":"one_case"},selected)):
                result=analyze(protocol_path,root)
            row=json.loads(result["features.json"])[0]
            self.assertEqual(row["status"],"unavailable")
            self.assertIsNone(row["features"])
            self.assertEqual(json.loads(result["summary.json"])["computed_sources"],0)
            self.assertEqual(json.loads(result["summary.json"])["selected_sources"],1)


if __name__=="__main__":
    unittest.main()
