"""Audit a BTCPay intake and deduplicate it against the pinned prior registries."""

import argparse
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "btcpay_source_intake_20261119_01"))

from audit import audit_transaction, development_matches, digest, require


def pinned_json(pin):
    path = (ROOT / pin["file"]).resolve()
    require(path.is_relative_to(ROOT), "Unexpected evidence path")
    content = path.read_bytes()
    require(digest(content) == pin["sha256"], f"Prior evidence fingerprint differs: {pin['file']}")
    return json.loads(gzip.decompress(content) if path.suffix == ".gz" else content)


def replay(archive, protocol):
    spec_bytes, archive_bytes = protocol.read_bytes(), archive.read_bytes()
    spec = json.loads(spec_bytes)
    evidence = json.loads(gzip.decompress(archive_bytes))
    require(evidence["schema_version"] == 1 and evidence["scope"] == spec["scope"],
            "Unexpected evidence scope")
    references = {entry["txid"]: entry for entry in spec["references"]}
    transactions = {entry["txid"]: entry for entry in evidence["transactions"]}
    require(1 <= len(references) <= 2
            and len(references) == len(spec["references"]) == len(evidence["transactions"])
            and transactions.keys() == references.keys(), "Repeated or unexpected transactions")

    pilot = pinned_json(spec["pilot"])
    pilot_addresses = set(pilot["address_witnesses"]["address_sha256"])
    previous = [record for pin in spec["previous_registries"]
                for record in pinned_json(pin)["records"]]
    previous_txids = {record["txid"] for record in previous}
    require(len(previous_txids) == len(previous) and not previous_txids & references.keys(),
            "Previously collected transaction repeated")
    old_addresses = pilot_addresses | {address for record in previous for address in record["address_sha256"]}
    records = [audit_transaction(transactions[txid], reference, spec)
               for txid, reference in references.items()]
    for record in records:
        if record["txid"] == pilot["reference"]["txid"]:
            require(pilot_addresses <= set(record["address_sha256"]), "Pilot witnesses differ")

    addresses = {address for record in records for address in record["address_sha256"]}
    shared = sum(record["distinct_input_addresses"] for record in records) - len(addresses)
    return {
        "scope": spec["scope"],
        "protocol_sha256": digest(spec_bytes),
        "archive": {"filename": archive.name, "sha256": digest(archive_bytes), "size_bytes": len(archive_bytes)},
        "evidence_kind": "reconciled_displayed_input_tables",
        "records": records,
        "displayed_input_rows": sum(record["displayed_input_rows"] for record in records),
        "distinct_input_addresses": len(addresses),
        "exact_address_matches_between_current_references": shared,
        "exact_address_matches_with_earlier_observations": len(addresses & old_addresses),
        "new_distinct_addresses": len(addresses - old_addresses),
        "cumulative_observed_addresses": len(addresses | old_addresses),
        "cumulative_documented_transactions": len(previous_txids | references.keys() | {pilot["reference"]["txid"]}),
        "exact_development_matches": development_matches(pilot, addresses, references),
        "direct_collection_api_requests": 0,
        "complete_individual_histories_added": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--protocol", type=Path, default=HERE / "protocol.json")
    args = parser.parse_args()
    print(json.dumps(replay(args.archive, args.protocol), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
