"""Failure-oriented tests for the external identity/transaction audit."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from audit_external_overlap import (
    COUNTERS, TX_COLUMNS, evidence_group, group_summary, markdown, pairwise_overlap,
    sha256, source_overlap, verify_history,
)


def output(address, value):
    return dict(scriptpubkey_address=address, value=value)


def transaction(txid, source, destination, value=100, parent="unobserved"):
    return dict(txid=txid, vin=[dict(is_coinbase=False, txid=parent, vout=0,
                                    prevout=output(source, value))],
                vout=[output(destination, value - 1)],
                status=dict(confirmed=True, block_time=1000))


def profile(address, transactions, group="incident", score=0.1):
    coaddresses = {v.get("scriptpubkey_address") for t in transactions for v in t["vout"]}
    coaddresses |= {(v.get("prevout") or {}).get("scriptpubkey_address")
                    for t in transactions for v in t["vin"]}
    coaddresses.discard(None)
    coaddresses.discard(address)
    return dict(address=address, evidence_group=group, _transactions={t["txid"]: t for t in transactions},
                _coaddresses=coaddresses, source_category_score=score,
                above_fixed_threshold=score > 0.15,
                source_record=dict(source_url="https://example.org/evidence"))


class ExternalOverlapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "history.json"

    def save_history(self, transactions=None, score=0.15):
        transactions = transactions if transactions is not None else [transaction("receipt", "donor", "focal")]
        counts = dict.fromkeys(COUNTERS, 0)
        counts["tx_count"] = len(transactions)
        for tx in transactions:
            for v in tx["vout"]:
                if v.get("scriptpubkey_address") == "focal":
                    counts["funded_txo_count"] += 1
                    counts["funded_txo_sum"] += v["value"]
            for vin in tx["vin"]:
                v = vin.get("prevout") or {}
                if v.get("scriptpubkey_address") == "focal":
                    counts["spent_txo_count"] += 1
                    counts["spent_txo_sum"] += v["value"]
        source = dict(address="focal", case_group="incident", source_url="https://example.org/evidence")
        history = dict(address="focal", collected_at="2026-10-14T00:00:00+00:00", source_record=source,
                       before=dict(address="focal", chain_stats=counts),
                       after=dict(address="focal", chain_stats=counts),
                       audit=dict(pagination_exhausted=True, coverage_complete_by_provider_counters=True,
                                  observed=counts), transactions=transactions)
        self.path.write_text(json.dumps(history))
        row = dict(address="focal", history_sha256=sha256(self.path), source_record=source,
                   collected_at=history["collected_at"], source_category_score=score,
                   threshold=0.15, above_fixed_threshold=score > 0.15)
        return history, row

    def rewrite(self, history, row):
        self.path.write_text(json.dumps(history))
        row["history_sha256"] = sha256(self.path)

    def test_coinbase_is_not_a_missing_sender_and_threshold_is_strict(self):
        coinbase = dict(txid="coinbase", vin=[dict(is_coinbase=True, prevout=None)],
                        vout=[output("focal", 500)], status=dict(confirmed=True))
        _, row = self.save_history([coinbase])
        result = verify_history(self.path, row)
        self.assertEqual(result["coinbase_inputs"], 1)
        self.assertEqual(result["decoded_coaddress_count"], 0)
        self.assertEqual(result["inputs_without_decoded_address"], 0)
        self.assertFalse(result["above_fixed_threshold"])

    def test_changed_bytes_rejected_before_interpreting_file(self):
        _, row = self.save_history()
        self.path.write_text("{}")
        with self.assertRaisesRegex(ValueError, "SHA256"):
            verify_history(self.path, row)

    def test_wrong_focal_identity_rejected(self):
        history, row = self.save_history()
        history["address"] = "another"
        self.rewrite(history, row)
        with self.assertRaisesRegex(ValueError, "address mismatch"):
            verify_history(self.path, row)

    def test_duplicate_transactions_rejected_even_with_matching_counters(self):
        tx = transaction("receipt", "donor", "focal")
        _, row = self.save_history([tx, tx])
        with self.assertRaisesRegex(ValueError, "Duplicate transaction"):
            verify_history(self.path, row)

    def test_unrelated_transaction_rejected(self):
        _, row = self.save_history([transaction("unrelated", "x", "y")])
        with self.assertRaisesRegex(ValueError, "Unrelated transaction"):
            verify_history(self.path, row)

    def test_unconfirmed_history_rejected(self):
        tx = transaction("pending", "donor", "focal")
        tx["status"]["confirmed"] = False
        _, row = self.save_history([tx])
        with self.assertRaisesRegex(ValueError, "Unconfirmed"):
            verify_history(self.path, row)

    def test_missing_noncoinbase_prevout_rejected(self):
        tx = transaction("receipt", "donor", "focal")
        tx["vin"][0]["prevout"] = None
        _, row = self.save_history([tx])
        with self.assertRaisesRegex(ValueError, "non-coinbase prevout"):
            verify_history(self.path, row)

    def test_provider_counter_drift_rejected(self):
        history, row = self.save_history()
        history["after"] = copy.deepcopy(history["after"])
        history["after"]["chain_stats"]["funded_txo_sum"] += 1
        self.rewrite(history, row)
        with self.assertRaisesRegex(ValueError, "reconciliation failed: after"):
            verify_history(self.path, row)

    def test_threshold_equal_is_not_an_alert(self):
        _, row = self.save_history(score=0.15)
        row["above_fixed_threshold"] = True
        with self.assertRaisesRegex(ValueError, "strict threshold"):
            verify_history(self.path, row)

    def test_shared_counterparty_does_not_merge_evidence_groups(self):
        a = profile("A", [transaction("a", "exchange", "A")], group="eff")
        b = profile("B", [transaction("b", "exchange", "B")], group="fsf")
        pairs, dependencies = pairwise_overlap([a, b])
        self.assertEqual(pairs[0]["shared_transaction_count"], 0)
        self.assertEqual(pairs[0]["shared_coaddresses"], ["exchange"])
        self.assertFalse(pairs[0]["same_evidence_group"])
        self.assertEqual(len(group_summary([a, b])), 2)
        self.assertEqual(dependencies, [])

    def test_common_transaction_detected_without_common_ownership_claim(self):
        tx = transaction("shared", "A", "B")
        pairs, _ = pairwise_overlap([profile("A", [tx]), profile("B", [tx])])
        self.assertEqual(pairs[0]["shared_txids"], ["shared"])
        self.assertTrue(pairs[0]["focal_a_in_b_coaddresses"])
        self.assertTrue(pairs[0]["focal_b_in_a_coaddresses"])

    def test_conflicting_shared_transaction_address_rejected(self):
        tx = transaction("shared", "A", "B")
        different = copy.deepcopy(tx)
        different["vout"][0]["scriptpubkey_address"] = "C"
        with self.assertRaisesRegex(ValueError, "Conflicting shared transaction"):
            pairwise_overlap([profile("A", [tx]), profile("B", [different])])

    def test_parent_child_dependency_even_when_no_shared_txid(self):
        parent = transaction("parent", "donor", "B")
        parent["vout"].append(output("bridge", 10))
        child = transaction("child", "bridge", "A", value=10, parent="parent")
        child["vin"][0]["vout"] = 1
        profiles = [profile("B", [parent]), profile("A", [child])]
        pairs, dependencies = pairwise_overlap(profiles)
        self.assertEqual(pairs[0]["shared_transaction_count"], 0)
        self.assertEqual(len(dependencies), 1)
        self.assertEqual(dependencies[0]["value_sat"], 10)
        self.assertEqual(dependencies[0]["history_pairs"], [dict(parent_history="B", child_history="A")])
        child["vin"][0]["prevout"]["value"] = 11
        with self.assertRaisesRegex(ValueError, "outpoint value/address mismatch"):
            pairwise_overlap(profiles)

    def test_source_extrema_overlap_without_focal_address_overlap(self):
        p = profile("pilot", [transaction("same", "train-peer", "pilot")])
        source = dict(address="train-peer", label="benign", transaction_number="1",
                      **{c: "same" for c in TX_COLUMNS})
        excluded = dict(address="excluded", label="Other", transaction_number="1",
                        **{c: "same" for c in TX_COLUMNS})
        result = source_overlap([p], {"BB.tsv": [source], "CB.tsv": [excluded]}, {"train-peer": "train"})
        b = result["BB.tsv"]["profiles"]["pilot"]
        self.assertFalse(b["focal_address_present"])
        self.assertEqual(b["extrema_transaction_match_count"], 1)
        self.assertEqual(b["matched_source_address_count"], 1)
        self.assertEqual(b["coaddress_matches_by_split"], {"train": 1})
        self.assertEqual(len(b["extrema_transaction_matches"][0]["source_records"]), 4)
        c = result["CB.tsv"]["profiles"]["pilot"]
        self.assertEqual(c["extrema_transaction_matches"][0]["source_records"][0]["benchmark_split"],
                         "excluded_from_benchmark")

    def test_group_counts_do_not_turn_six_addresses_into_six_incidents(self):
        ps = [profile(str(i), [], group="fbi", score=0.1 if i < 3 else 0.2) for i in range(6)]
        groups = group_summary(ps)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["addresses"], 6)
        self.assertEqual(groups[0]["above_fixed_threshold"], 3)
        with self.assertRaisesRegex(ValueError, "Missing explicit evidence group"):
            evidence_group(dict(address="A"))

    def test_batch_corecipient_overlap_preserves_roles_and_coverage(self):
        tx = transaction("batch", "sender", "pilot", value=1000)
        tx["vout"] = [output("pilot", 547), output("train-peer", 400)]
        p = profile("pilot", [tx])
        record = dict(address="train-peer", label="benign", transaction_number="1",
                      **{c: "" for c in TX_COLUMNS})
        record["min_received_transaction_id"] = "batch"
        result = source_overlap([p], {"BB.tsv": [record]}, {"train-peer": "train"})["BB.tsv"]
        match = result["profiles"]["pilot"]["extrema_transaction_matches"][0]
        self.assertEqual(match["output_count"], 2)
        self.assertEqual(match["focal_observed_roles"], dict(input_count=0, input_value_sat=0,
                         output_count=1, output_value_sat=547))
        self.assertEqual(match["source_records"][0]["observed_roles"]["input_count"], 0)
        self.assertTrue(match["source_records"][0]["observed_on_expected_side"])
        self.assertEqual(result["distinct_nonempty_extrema_txids"], 1)
        self.assertEqual(result["nonempty_extrema_by_column"]["max_sent_transaction_id"], 0)

    def test_rendered_report_computes_findings_for_other_inputs(self):
        tx = transaction("shared", "A", "B")
        ps = [profile("A", [tx], group="one"), profile("B", [tx], group="two")]
        pairs, dependencies = pairwise_overlap(ps)
        report = dict(scope=dict(addresses=2, distinct_confirmed_transactions=1, evidence_groups=2,
                                 pairwise_comparisons=1), executed_at="fixture", profiles=ps,
                      source_overlap=source_overlap(ps, {"BB.tsv": [], "CB.tsv": []}, {}),
                      source_sha256={"BB.tsv": "fixture", "CB.tsv": "fixture"},
                      split_membership_counts=dict(train=0, validation=0, reserved_test=0),
                      descriptive_evidence_groups=group_summary(ps), pairwise_overlaps=pairs,
                      cross_history_transaction_dependencies=dependencies, limitations=[],
                      score_reports=[dict(file="other_scores.json")])
        text = markdown(report)
        self.assertIn("0 pilot histories share 0 source-extremum transaction IDs", text)
        self.assertIn("1 pairs share at least one transaction ID", text)
        self.assertIn("--scores other_scores.json", text)
        self.assertNotIn("FSF", text)
        self.assertNotIn("BTCPay", text)
        self.assertNotIn("eleven", text)


if __name__ == "__main__":
    unittest.main()
