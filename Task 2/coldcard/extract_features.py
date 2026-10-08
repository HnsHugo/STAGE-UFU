"""Extract block transaction features, preserving attribution uncertainty.
Usage: python extract_features.py blocks parents.json features_output
The output directory must not exist. Only manifest status=complete is usable.
"""
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
from audit_coldcard_parents import transactions, SEEDS, SOURCE

FIELDS = ["txid", "block_height", "relation", "input_count", "output_count",
          "distinct_input_addresses", "distinct_output_addresses",
          "input_address_missing_count", "output_address_missing_count",
          "input_total_sat", "output_total_sat", "fee_sat", "vsize_vb",
          "fee_rate_sat_vb", "version", "lock_time", "is_coinbase",
          "min_output_sat", "max_output_sat", "zero_value_outputs"]

def feature_row(height, tx, candidates):
    inputs = [i.get("prev_out", {}) for i in tx["inputs"]]
    outputs = tx["out"]
    coinbase = len(inputs) == 1 and inputs[0].get("tx_index") == 0 and inputs[0].get("n") == 4294967295
    vsize = math.ceil(tx["weight"] / 4)
    relation = ("source_attributed" if tx["hash"] in SEEDS else
                "direct_parent_candidate" if tx["hash"] in candidates else "unattributed")
    values = [o["value"] for o in outputs]
    return dict(zip(FIELDS, [
        tx["hash"], height, relation, len(inputs), len(outputs),
        len({i["addr"] for i in inputs if i.get("addr")}),
        len({o["addr"] for o in outputs if o.get("addr")}),
        sum(not i.get("addr") for i in inputs),
        sum(not o.get("addr") for o in outputs),
        None if coinbase else sum(i["value"] for i in inputs),
        sum(values), tx["fee"], vsize,
        None if coinbase or not vsize else tx["fee"] / vsize,
        tx["ver"], tx["lock_time"], int(coinbase),
        min(values) if values else None, max(values) if values else None,
        sum(v == 0 for v in values),
    ]))

def extract(blocks, parents, destination):
    raw = Path(parents).read_bytes()
    audit = json.loads(raw)
    candidates = {r["txid"] for r in audit["parents"]}
    if len(candidates) != audit["parent_transactions_found"]:
        raise ValueError("Parent count mismatch or duplicate TXIDs.")
    out = Path(destination)
    out.mkdir(exist_ok=False)
    manifest = {
        "status": "incomplete", "source": SOURCE,
        "parent_report_sha256": hashlib.sha256(raw).hexdigest(),
        "warning": "Relations are not theft/hardware labels. Unattributed is not legitimate.",
        "model_exclusions": ["txid", "block_height", "relation"],
        "feature_timing": "Confirmed transaction properties; no future spent-status features.",
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    counts = {}
    total = 0
    with gzip.open(out / "transactions.csv.gz", "wt", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for height, tx in transactions(blocks):
            row = feature_row(height, tx, candidates)
            writer.writerow(row)
            counts[row["relation"]] = counts.get(row["relation"], 0) + 1
            total += 1
    if total != 493571 or counts.get("source_attributed") != 5 or counts.get("direct_parent_candidate") != len(candidates):
        raise ValueError("Coverage differs from inspected archive; output remains incomplete.")
    manifest.update(status="complete", transaction_count=total, relation_counts=counts)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: python extract_features.py blocks parents.json features_output")
    extract(*sys.argv[1:])
