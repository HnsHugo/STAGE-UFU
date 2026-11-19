"""Reconcile the saved explorer observations and export the hashed source registry."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ADDRESS = re.compile(r"(?:bc1[02-9ac-hj-np-z]{11,87}|[13][1-9A-HJ-NP-Za-km-z]{25,34})")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def audit_transaction(transaction, reference, scope):
    require(all(transaction[key] == value for key, value in reference.items()),
            "Transaction differs from its pinned reference")
    low, high = scope["height_window_inclusive"]
    require(low <= transaction["block_height"] <= high, "Reference outside the intake window")
    require(transaction["collector"] == scope["collector"], "Collector differs")
    require(transaction["missing"] == transaction["unhandled"] == []
            and transaction["final_amounts_equal"] is True, "Incomplete or ambiguous displayed table")
    rows = transaction["input_rows"]
    positions = [entry["row"] for entry in rows]
    require(positions == sorted(set(positions)) and positions,
            "Missing or repeated input positions")
    require(transaction["input_table_start_line"] <= positions[0]
            <= positions[-1] < transaction["output_line"] < transaction["fee_line"],
            "Input positions lie outside the confirmed table")
    require(all(ADDRESS.fullmatch(entry["address"]) and type(entry["value_sat"]) is int
                and entry["value_sat"] > 0 for entry in rows), "Invalid input address or value")
    total = sum(entry["value_sat"] for entry in rows)
    output, fee = transaction["collector_output_sat"], transaction["fee_sat"]
    require(total == transaction["input_total_sat"] == output + fee and output > 0 and fee >= 0,
            "Values fail to reconcile")
    addresses = {digest(entry["address"].encode()) for entry in rows}
    return {**reference, "displayed_input_rows": len(rows), "distinct_input_addresses": len(addresses),
            "input_total_sat": total, "collector_output_sat": output, "fee_sat": fee,
            "address_sha256": sorted(addresses)}


def development_matches(pilot, addresses, reference_txids):
    matches = {}
    references = {digest(txid.encode()) for txid in reference_txids}
    for name, pin in pilot["development_pins"].items():
        dataset = (ROOT / pin["file"]).resolve()
        require(dataset.is_relative_to(ROOT), "Unexpected development input path")
        content = dataset.read_bytes()
        require(digest(content) == pin["sha256"], f"Development fingerprint differs for {name}")
        rows = json.loads(gzip.decompress(content))["rows"]
        key = "payment_txid_sha256" if name == "coldcard" else "reference_txid_sha256"
        matches[name] = {
            "selected_rows": len(rows),
            "address_matches": len(addresses & {row["address_sha256"] for row in rows}),
            "reference_txid_matches": len(references & {row[key] for row in rows}),
        }
    return matches


def build(archive):
    policy = (HERE / "protocol.json").read_bytes()
    scope = json.loads(policy)
    evidence_bytes = archive.read_bytes()
    evidence = json.loads(gzip.decompress(evidence_bytes))
    require(evidence["schema_version"] == 1 and evidence["scope"] == scope["scope"],
            "Unexpected evidence format or scope")
    transactions = {transaction["txid"]: transaction for transaction in evidence["transactions"]}
    require(len(transactions) == len(evidence["transactions"]) == len(scope["references"])
            and transactions.keys() == {reference["txid"] for reference in scope["references"]},
            "Unexpected or repeated reference transaction")
    records = [audit_transaction(transactions[reference["txid"]], reference, scope)
               for reference in scope["references"]]
    first, second = (set(record["address_sha256"]) for record in records)
    addresses = first | second
    shared = first & second
    pilot_bytes = (ROOT / scope["pilot_audit"]).read_bytes()
    pilot = json.loads(pilot_bytes)
    previously_visible = set(pilot["address_witnesses"]["address_sha256"])
    require(pilot["reference"]["txid"] not in transactions, "Previously audited transaction repeated")
    return {
        "scope": scope["scope"],
        "protocol_sha256": digest(policy),
        "archive": {"filename": archive.name, "sha256": digest(evidence_bytes), "size_bytes": len(evidence_bytes)},
        "pilot_audit_sha256": digest(pilot_bytes),
        "evidence_kind": "reconciled_displayed_input_tables",
        "records": records,
        "displayed_input_rows": sum(record["displayed_input_rows"] for record in records),
        "distinct_input_addresses": len(addresses),
        "new_address_digests_excluding_visible_pilot": len(addresses - previously_visible),
        "distinct_addresses_including_visible_pilot": len(addresses | previously_visible),
        "exact_address_matches_between_new_references": len(shared),
        "exact_address_matches_with_visible_pilot": len(addresses & previously_visible),
        "observed_components_in_new_references": 1 if shared else 2,
        "exact_development_matches": development_matches(pilot, addresses, transactions),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.archive), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
