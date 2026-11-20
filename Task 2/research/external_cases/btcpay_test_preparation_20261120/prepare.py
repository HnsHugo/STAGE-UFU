"""Build the private BTCPay reference plan from pinned, locally saved intakes."""

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "btcpay_source_intake_20261119_01"))
sys.path.insert(0, str(HERE.parent / "btcpay_source_intake_20261119_02"))
sys.path.insert(0, str(HERE.parent.parent / "coldcard"))

from audit import build, development_matches, digest, require
from replay import pinned_json, replay
from prepayment_pilot import FEATURE_NAMES
from source_cohort import atomic_write


def verified_intake(pins, archives, first):
    spec = pinned_json(pins["protocol"])
    registry = pinned_json(pins["registry"])
    checkpoint = registry["archive"]
    name = checkpoint["filename"]
    require(Path(name).name == name, "Invalid evidence basename")
    archive = archives / name
    saved = archive.read_bytes()
    require(len(saved) == checkpoint["size_bytes"] and digest(saved) == checkpoint["sha256"],
            f"Changed or incomplete intake archive: {name}")
    reference_path = ROOT / pins["protocol"]["file"]
    reproduced = build(archive) if first else replay(archive, reference_path)
    require(reproduced == registry, f"Intake replay differs from published registry: {name}")
    evidence = json.loads(gzip.decompress(saved))
    require(evidence["scope"] == spec["scope"], f"Intake scope differs: {name}")
    return spec, evidence["transactions"], checkpoint


def reference_rows(transaction):
    slots = Counter(row["address"] for row in transaction["input_rows"])
    amounts = Counter()
    for row in transaction["input_rows"]:
        amounts[row["address"]] += row["value_sat"]
    reference = transaction["txid"]
    reference_hash = digest(reference.encode())
    for address in sorted(slots):
        yield {
            "address": address,
            "address_sha256": digest(address.encode()),
            "payment_txid": reference,
            "payment_txid_sha256": reference_hash,
            "cutoff_height": transaction["block_height"],
            "cutoff_block_hash": transaction["block_hash"],
            "registry_input_slots": slots[address],
            "reference_input_value_sat": amounts[address],
            "observed_co_input_group": reference_hash,
            "btcpay_reference_source_membership": 1,
            "compromise_label": None,
            "hardware_label": None,
        }


def prepare(archives):
    protocol_bytes = (HERE / "protocol.json").read_bytes()
    protocol = json.loads(protocol_bytes)
    pilot = pinned_json(protocol["pilot"])
    models = protocol["frozen_models"]
    require(digest((ROOT / models["file"]).read_bytes()) == models["sha256"], "Frozen model changed")
    reference_ids = {pilot["reference"]["txid"]}
    witnesses = set(pilot["address_witnesses"]["address_sha256"])
    first_height, last_height = protocol["height_window_inclusive"]
    rows, checkpoints = [], []
    block_hashes = {}
    input_rows = 0
    for index, pins in enumerate(protocol["intakes"]):
        spec, transactions, checkpoint = verified_intake(pins, archives, first=(index == 0))
        require(spec["collector"] == protocol["collector"], "Different intake collector")
        for tx in transactions:
            require(tx["txid"] not in reference_ids, "Repeated payment across frozen intakes")
            require(first_height <= tx["block_height"] <= last_height, "Reference outside BTCPay window")
            previous_hash = block_hashes.setdefault(tx["block_height"], tx["block_hash"])
            require(previous_hash == tx["block_hash"], "Conflicting block anchors at one height")
            reference_ids.add(tx["txid"])
            input_rows += len(tx["input_rows"])
            rows.extend(reference_rows(tx))
        checkpoints.append(checkpoint)

    rows.sort(key=lambda row: (row["cutoff_height"], row["payment_txid"], row["address_sha256"]))
    for index, row in enumerate(rows, 1):
        row["pilot_id"] = f"btcpay_case_{index:04d}"
    addresses = {row["address_sha256"] for row in rows}
    matches = development_matches(pilot, addresses | witnesses, reference_ids)
    require(all(match["address_matches"] == 0 and match["reference_txid_matches"] == 0
                for match in matches.values()), "Exact development overlap needs review before pilot selection")

    # One preselected source per reference block. Its rank uses only identifiers
    # and is independent of history availability and model scores.
    design = protocol["candidate_pilot"]
    salt = design["salt"]
    by_block = {}
    for row in sorted(rows, key=lambda row: (
        digest((salt + row["payment_txid_sha256"] + row["address_sha256"]).encode()), row["pilot_id"]
    )):
        by_block.setdefault(row["cutoff_height"], row)
    blocks = [{
        "height": height,
        "hash": row["cutoff_block_hash"],
        "case_source_id": row["pilot_id"],
        "desired_comparisons": design["comparison_quota_per_selected_case"],
    } for height, row in sorted(by_block.items())]
    coverage = {
        "archives_replayed": len(checkpoints),
        "payments_documented": len(reference_ids),
        "payments_with_complete_input_tables": len(reference_ids) - 1,
        "reconciled_input_rows": input_rows,
        "distinct_addresses_observed": len(addresses | witnesses),
        "distinct_addresses_from_complete_input_tables": len(addresses),
        "prepared_source_reference_pairs": len(rows),
        "partial_pilot_witnesses_preserved": len(witnesses),
        "candidate_pilot_sources": len(blocks),
        "comparison_quota": sum(block["desired_comparisons"] for block in blocks),
        "comparisons_selected": 0,
        "complete_btcpay_prefixes_in_catalogue": 0,
        "model_evaluations": 0,
        "exact_development_overlap": matches,
    }
    return {
        "schema_version": 1,
        "protocol_sha256": digest(protocol_bytes),
        "intake_archives": checkpoints,
        "source_reference_pairs": rows,
        "partial_pilot": pilot["address_witnesses"],
        "pilot_blocks": blocks,
        "predictors": list(FEATURE_NAMES),
        "coverage": coverage,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", type=Path, help="Directory holding the verified intake gzip files")
    parser.add_argument("private_output", type=Path, help="New private catalogue destination")
    args = parser.parse_args()
    require(not args.private_output.resolve().is_relative_to(ROOT), "Keep raw catalogue outside Git")
    require(not args.private_output.exists(), "Private catalogue already exists")
    catalogue = prepare(args.archives)
    content = gzip.compress((json.dumps(catalogue, sort_keys=True) + "\n").encode(), mtime=0)
    atomic_write(args.private_output, content)
    print(json.dumps({"catalogue_sha256": digest(content), **catalogue["coverage"]}, indent=2))


if __name__ == "__main__":
    main()
