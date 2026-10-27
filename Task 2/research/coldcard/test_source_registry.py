"""Check roles, windows, outpoints and missingness in source reconstruction."""
import copy
from datetime import datetime
import unittest

from build_source_registry import build


def fixture():
    start = int(datetime.fromisoformat("2026-07-30T00:00:00+00:00").timestamp())
    protocol = dict(collector_address="collector", case_id="single_case",
                    network="bitcoin-mainnet", reviewed_on="2026-10-27",
                    candidate_window=dict(start_utc="2026-07-30T00:00:00+00:00",
                                          end_exclusive_utc="2026-07-31T00:00:00+00:00"))
    def tx(tid, when, inputs, outputs, fee):
        return dict(txid=tid, status=dict(confirmed=True, block_hash="f"*64,
                                         block_height=1, block_time=when),
                    vin=inputs, vout=outputs, fee=fee)
    def inp(previous, n, address, value):
        return dict(txid=previous, vout=n, prevout=dict(scriptpubkey_address=address, value=value))
    transactions = [tx("1"*64, start,
                       [inp("a"*64, 0, "source", 60), inp("a"*64, 1, "source", 40)],
                       [dict(scriptpubkey_address="collector", value=99)], 1),
                    tx("2"*64, start+86400, [inp("b"*64, 0, "later_source", 8)],
                       [dict(scriptpubkey_address="collector", value=7)], 1),
                    tx("3"*64, start+86401, [inp("1"*64, 0, "collector", 99)],
                       [dict(scriptpubkey_address="destination", value=98)], 1)]
    counters = dict(tx_count=3, funded_txo_count=2, funded_txo_sum=106,
                    spent_txo_count=1, spent_txo_sum=99)
    history = dict(address="collector", provider="https://example.invalid/api",
                   collected_at="2026-10-19T00:00:00+00:00", transactions=transactions,
                   audit=dict(pagination_exhausted=True),
                   before=dict(address="collector", chain_stats=counters),
                   after=dict(address="collector", chain_stats=copy.deepcopy(counters)))
    return history, protocol


class SourceRegistryTests(unittest.TestCase):
    def test_repeated_inputs_are_one_address_and_exact_outpoints(self):
        history, protocol = fixture()
        rows, evidence, summary = build(history, protocol)
        source = next(r for r in rows if r["address"] == "source")
        self.assertEqual(source["spent_previous_output_count"], 2)
        self.assertEqual(source["known_spent_input_value_sat"], 100)
        self.assertEqual(source["distinct_payment_count"], 1)
        self.assertEqual([e["previous_outpoint"]["vout"] for e in evidence[:2]], [0, 1])
        self.assertEqual(summary["source_address_count"], 2)
        self.assertEqual(summary["incident_group_count"], 1)
        self.assertEqual(evidence[0]["collector_receipts"][0]["observed_spending_txid"], "3"*64)

    def test_roles_and_device_labels_do_not_propagate(self):
        rows, _, summary = build(*fixture())
        self.assertNotIn("collector", {r["address"] for r in rows})
        self.assertNotIn("destination", {r["address"] for r in rows})
        for row in rows:
            self.assertEqual(row["compromise_status"], "unknown")
            self.assertEqual(row["hardware_control"], "unknown")
            self.assertIsNone(row["supervised_compromise_label"])
            self.assertIsNone(row["label_available_at"])
            self.assertIsNone(row["entity_id"])
        self.assertFalse(summary["supervised_training_ready"])

    def test_window_is_start_inclusive_end_exclusive(self):
        rows, _, summary = build(*fixture())
        self.assertEqual(summary["groups"]["candidate_window"]["receipts"], 1)
        later = next(r for r in rows if r["address"] == "later_source")
        self.assertEqual(later["scopes"], ["outside_candidate_window"])
        self.assertIsNone(later["supervised_compromise_label"])

    def test_missing_prevout_retains_evidence_without_inventing_source(self):
        history, protocol = fixture()
        history["transactions"][1]["vin"][0]["prevout"] = None
        rows, evidence, summary = build(history, protocol)
        self.assertEqual(len(rows), 1)
        self.assertIsNone(evidence[-1]["source_address"])
        self.assertIsNone(evidence[-1]["spent_input_value_sat"])
        self.assertEqual(summary["groups"]["outside_candidate_window"]["missing_prevouts"], 1)

    def test_duplicate_outpoint_and_missing_previous_id_rejected(self):
        history, protocol = fixture()
        history["transactions"][0]["vin"][1]["vout"] = 0
        with self.assertRaisesRegex(ValueError, "Duplicate spent outpoint"):
            build(history, protocol)
        history, protocol = fixture()
        history["transactions"][0]["vin"][0].pop("txid")
        with self.assertRaisesRegex(ValueError, "previous TXID"):
            build(history, protocol)

    def test_integer_values_and_fee_reconciliation(self):
        history, protocol = fixture()
        history["transactions"][0]["vin"][0]["prevout"]["value"] = 60.0
        with self.assertRaisesRegex(ValueError, "integer satoshis"):
            build(history, protocol)
        history, protocol = fixture()
        history["transactions"][0]["fee"] = 2
        with self.assertRaisesRegex(ValueError, "input/output/fee mismatch"):
            build(history, protocol)

    def test_unstable_or_incomplete_history_rejected(self):
        history, protocol = fixture()
        history["audit"]["pagination_exhausted"] = False
        with self.assertRaisesRegex(ValueError, "complete collector history"):
            build(history, protocol)

    def test_multi_address_inputs_do_not_allocate_receipt_or_merge_owners(self):
        history, protocol = fixture()
        history["transactions"][0]["vin"][1]["prevout"]["scriptpubkey_address"] = "other_source"
        rows, evidence, summary = build(history, protocol)
        self.assertEqual(summary["groups"]["candidate_window"]["multi_source_address_transactions"], 1)
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(e["collector_value_allocated_to_this_input_sat"] is None for e in evidence))
        self.assertTrue(all(r["entity_id"] is None for r in rows))

    def test_transaction_order_does_not_create_labels_or_extra_addresses(self):
        history, protocol = fixture()
        first = build(history, protocol)
        history["transactions"].reverse()
        second = build(history, protocol)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
