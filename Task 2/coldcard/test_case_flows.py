"""Flow accounting guards: exact prevouts, distinct sources, and double counts."""
import unittest
import copy
import gzip
import io
import json
from pathlib import Path
import tempfile
from contextlib import redirect_stdout
from unittest.mock import patch

from analyze_case_flows import (SEEDS, SOURCE, address_summary, btc, check_parent_report,
                                collect, collect_outspends, reconcile_received_prevouts,
                                seed_summary)


class CaseFlowsTests(unittest.TestCase):
    def test_signed_satoshi_format_is_exact(self):
        self.assertEqual(btc(-1), "-0.00000001")
        self.assertEqual(btc(-100000001), "-1.00000001")
        self.assertEqual(btc(0), "0.00000000")

    def test_receipts_count_outputs_and_sources_without_duplicating_addresses(self):
        transactions = [
            dict(txid="fund", block_time=10,
                 inputs=[dict(tx_index=1, n=0, addr="source", value=15),
                         dict(tx_index=2, n=0, addr="source", value=10)],
                 outputs=[dict(n=0, addr="target", value=8),
                          dict(n=1, addr="target", value=12),
                          dict(n=2, addr="change", value=4)]),
            dict(txid="spend", block_time=20,
                 inputs=[dict(tx_index=3, n=0, addr="target", value=8)],
                 outputs=[dict(n=0, addr="target", value=2),
                          dict(n=1, addr="next", value=5)]),
        ]
        r = address_summary(transactions, "target")
        self.assertEqual(r["received_sat"], 22)
        self.assertEqual(r["received_output_count"], 3)
        self.assertEqual(r["spent_input_sat"], 8)
        self.assertEqual(r["observed_receipts_minus_spent_sat"], 14)
        self.assertEqual(r["funding_transaction_distinct_input_addresses"], 2)
        self.assertEqual(r["self_receipt_output_count"], 1)

    def test_duplicate_history_transactions_rejected(self):
        tx = dict(txid="x", block_time=1, inputs=[], outputs=[])
        with self.assertRaisesRegex(ValueError, "Duplicate transaction"):
            address_summary([tx, tx], "target")

    def test_double_spent_prevout_rejected(self):
        txs = [dict(txid=tid, block_time=1,
                    inputs=[dict(tx_index=4, n=1, addr="target", value=2)], outputs=[])
               for tid in ("first", "second")]
        with self.assertRaisesRegex(ValueError, "duplicate consumed"):
            address_summary(txs, "target")

    def test_coinbase_null_prevout_does_not_crash_or_claim_source_address(self):
        tx = dict(txid="coinbase", vin=[dict(is_coinbase=True, prevout=None)],
                  vout=[dict(scriptpubkey_address="target", value=100)],
                  status=dict(block_time=1))
        r = address_summary([tx], "target", esplora=True)
        self.assertEqual(r["received_sat"], 100)
        self.assertEqual(r["funding_transaction_distinct_input_addresses"], 0)
        self.assertEqual(r["funding_transaction_missing_input_address_slots"], 1)

    def case(self):
        seed = dict(txid="seed", height=10, block_time=300,
                    provider_transaction_time=290, fee_sat=1,
                    inputs=[dict(tx_index=2, n=1, addr="collector", value=9),
                            dict(tx_index=3, n=0, addr="collector", value=7)],
                    outputs=[dict(n=0, addr="destination", value=15)])
        parent = dict(txid="parent", index=2, block_time=200,
                      provider_transaction_time=190,
                      inputs=[dict(addr="source", value=51), dict(addr="source", value=9)],
                      outputs=[dict(n=0, addr="elsewhere", value=50),
                               dict(n=1, addr="collector", value=9)])
        return seed, {2: parent}

    def test_specific_prevout_value_not_total_parent_value_and_missing_coverage(self):
        seed, parents = self.case()
        r = seed_summary(seed, parents)
        self.assertEqual(r["recovered_parent_output_sat"], 9)
        self.assertEqual(r["missing_parent_output_sat"], 7)
        self.assertEqual(r["parent_transactions_recovered"], 1)
        self.assertEqual(r["parent_transactions_missing"], 1)
        self.assertEqual(r["recovered_funding_distinct_input_addresses"], 1)
        self.assertEqual(r["first_recovered_funding_to_seed_provider_seconds"], 100)
        self.assertEqual(r["input_sat"], r["output_sat"] + r["fee_sat"])

    def test_parent_prevout_disagreement_is_not_silently_accepted(self):
        seed, parents = self.case()
        parents[2]["outputs"][1]["value"] = 8
        with self.assertRaisesRegex(ValueError, "differs from seed prevout"):
            seed_summary(seed, parents)

    def test_invalid_fee_accounting_rejected(self):
        seed, parents = self.case()
        seed["fee_sat"] = 2
        with self.assertRaisesRegex(ValueError, "reconciliation failed"):
            seed_summary(seed, parents)

    def test_multiple_seed_inputs_from_same_parent_count_parent_once(self):
        seed, parents = self.case()
        seed["inputs"][1] = dict(tx_index=2, n=2, addr="collector", value=7)
        parents[2]["outputs"].append(dict(n=2, addr="collector", value=7))
        r = seed_summary(seed, parents)
        self.assertEqual(r["parent_output_count"], 2)
        self.assertEqual(r["distinct_parent_transactions_requested"], 1)
        self.assertEqual(r["parent_transactions_recovered"], 1)
        self.assertEqual(r["collectors"][0]["recovered_parent_count"], 1)

    def complete_history(self):
        out = dict(scriptpubkey_address="target", scriptpubkey="0014abcd", value=10)
        received = dict(txid="fund", vin=[], vout=[out],
                        status=dict(block_height=1, block_time=10))
        spent = dict(txid="spend", vin=[dict(txid="fund", vout=0, prevout=copy.deepcopy(out))],
                     vout=[], status=dict(block_height=2, block_time=20))
        return [received, spent]

    def test_spent_prevouts_match_actual_received_outputs(self):
        result = reconcile_received_prevouts(self.complete_history(), "target")
        self.assertEqual(result["consumed_outpoints_reconciled"], 1)
        self.assertEqual(result["consumed_sat"], 10)
        self.assertFalse(result["cryptographic_inclusion_verified"])

    def test_prevout_corruption_rejected_even_when_aggregate_counter_could_match(self):
        for name in ("txid", "vout", "value", "script", "height", "duplicate"):
            history = self.complete_history()
            item = history[1]["vin"][0]
            with self.subTest(corruption=name):
                if name == "txid":
                    item["txid"] = "not_in_history"
                elif name == "vout":
                    item["vout"] = -1
                elif name == "value":
                    item["prevout"]["value"] = 11
                elif name == "script":
                    item["prevout"]["scriptpubkey"] = "0014ffff"
                elif name == "height":
                    history[0]["status"]["block_height"] = 3
                else:
                    history[1]["vin"].append(copy.deepcopy(item))
                with self.assertRaises(ValueError):
                    reconcile_received_prevouts(history, "target")

    def parent_report(self):
        seed, parents = self.case()
        seed["txid"] = sorted(SEEDS)[0]
        parents[2]["height"] = 9
        data = dict(source=SOURCE, source_attributed_seeds_found=[seed["txid"]],
            source_attributed_seeds_missing=sorted(SEEDS - {seed["txid"]}),
            distinct_parent_indices_requested=2, parent_transactions_found=1,
            parent_transactions_missing=1,
            parents=[dict(txid="parent", height=9, input_count=2, output_count=2,
                          distinct_input_addresses=1, spent_output_indices=[1],
                          label="unknown", relationship="direct_parent_of_source_attributed_transaction")])
        return data, {seed["txid"]: seed}, parents

    def test_parent_report_rows_are_reconstructed_not_just_counted(self):
        data, seeds, parents = self.parent_report()
        self.assertEqual(check_parent_report(data, seeds, parents)["rows_reconciled"], 1)
        data["parents"][0]["txid"] = "another_parent_same_count"
        with self.assertRaisesRegex(ValueError, "rows differ"):
            check_parent_report(data, seeds, parents)

    def test_parent_report_rejects_promoting_unknown_label_to_theft(self):
        data, seeds, parents = self.parent_report()
        data["parents"][0]["label"] = "stolen"
        with self.assertRaisesRegex(ValueError, "rows differ"):
            check_parent_report(data, seeds, parents)

    def test_collector_matches_file_encoding_and_refuses_overwrite(self):
        stats = dict(tx_count=0, funded_txo_count=0, spent_txo_count=0,
                     funded_txo_sum=0, spent_txo_sum=0)
        counter = dict(address="target", chain_stats=stats)
        for suffix in (".json", ".json.gz"):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / ("history" + suffix)
                with patch("analyze_case_flows.get", side_effect=[counter, [], counter]), redirect_stdout(io.StringIO()):
                    collect(output, "target", 2)
                raw = output.read_bytes()
                result = json.loads(gzip.decompress(raw) if suffix.endswith(".gz") else raw)
                self.assertTrue(result["audit"]["coverage_complete_by_provider_counters"])
                with patch("analyze_case_flows.get") as request:
                    with self.assertRaisesRegex(ValueError, "already exists"):
                        collect(output, "target", 2)
                    request.assert_not_called()
                self.assertEqual(output.read_bytes(), raw)

    def test_outspend_collector_preserves_failed_queries_as_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            report, output = Path(directory) / "report.json", Path(directory) / "observed.json"
            report.write_text(json.dumps(dict(source_attributed_seeds=[
                dict(txid="a" * 64, outputs=[dict(index=0, address="first"),
                                           dict(index=1, address="second")])])))
            with patch("analyze_case_flows.get", side_effect=[dict(spent=False), OSError("unavailable")]), redirect_stdout(io.StringIO()):
                collect_outspends(report, output)
            data = json.loads(output.read_text())
            self.assertFalse(data["queries"][0]["response"]["spent"])
            self.assertNotIn("response", data["queries"][1])
            self.assertEqual(data["queries"][1]["error"], "unavailable")
            self.assertTrue(all(q["collected_at"] for q in data["queries"]))
            with patch("analyze_case_flows.get") as request:
                with self.assertRaisesRegex(ValueError, "already exists"):
                    collect_outspends(report, output)
                request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
