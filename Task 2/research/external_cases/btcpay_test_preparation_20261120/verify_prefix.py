"""Audit a privately saved confirmed-history tail and compute the fixed 14 features."""

import argparse
import gzip
import json
from pathlib import Path

from prepare import digest, require, ROOT
from audit_reference_tail import independent_features
from collect_reference_tail import tail_check
from source_cohort import atomic_write


def verified_prefix(record, capture):
    require(capture["address"] == record["address"], "Recorded address differs from reference plan")
    require(capture["pages"], "Missing saved cursor pages")
    cursor = record["payment_txid"]
    transactions = []
    exhausted = False
    for page in capture["pages"]:
        require(not exhausted and page["after_txid"] == cursor, "Invalid native cursor sequence")
        txs = page["transactions"]
        require(isinstance(txs, list) and len(txs) <= 25, "Invalid saved cursor page")
        if not txs:
            exhausted = True
            continue
        transactions.extend(txs)
        cursor = txs[-1]["txid"]
    result = tail_check(record, capture["reference"], transactions, exhausted,
                        capture["reference_after"], capture["parent_statuses"])
    if result["status"] == "complete_prior_prefix":
        counted = independent_features(record, {"transactions": transactions})
        require(result["features"] == counted, "Independent recount of 14 predictors differs")
    return result


def read_verified(path, expected):
    raw = path.read_bytes()
    require(digest(raw) == expected, "Saved file fingerprint differs")
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("catalogue_sha256")
    parser.add_argument("source_id")
    parser.add_argument("capture", type=Path)
    parser.add_argument("capture_sha256")
    parser.add_argument("private_output", type=Path)
    args = parser.parse_args()
    require(not args.private_output.resolve().is_relative_to(ROOT), "Keep prefix evidence outside Git")
    require(not args.private_output.exists(), "Prefix result already exists")
    catalogue = read_verified(args.catalogue, args.catalogue_sha256)
    matches = [row for row in catalogue["source_reference_pairs"] if row["pilot_id"] == args.source_id]
    require(len(matches) == 1, "Source must have one frozen reference in the catalogue")
    record = matches[0]
    capture = read_verified(args.capture, args.capture_sha256)
    result = verified_prefix(record, capture)
    result.update(source_id=args.source_id, cutoff_height=record["cutoff_height"],
                  cutoff_block_hash=record["cutoff_block_hash"],
                  address_sha256=record["address_sha256"],
                  reference_txid_sha256=record["payment_txid_sha256"],
                  evidence_sha256=args.capture_sha256, catalogue_sha256=args.catalogue_sha256)
    content = gzip.compress((json.dumps(result, sort_keys=True) + "\n").encode(), mtime=0)
    atomic_write(args.private_output, content)
    print(json.dumps({"source_id": args.source_id, "status": result["status"], "sha256": digest(content)}))


if __name__ == "__main__":
    main()
