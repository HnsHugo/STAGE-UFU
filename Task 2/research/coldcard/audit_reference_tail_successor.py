"""Audit later successors with dynamic predecessor counts and a schema-v2 view."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path

from build_source_registry import digest, json_bytes
import audit_reference_tail as prior_audit
import collect_reference_tail as tail
from source_cohort import atomic_write


def audit(q, output, work):
    proto = json.loads(q.read_bytes())
    for value in proto["inputs"].values():
        if digest((q.parent / value["file"]).read_bytes()) != value["sha256"]:
            raise ValueError("Pinned continuation input changed")
    baseline_raw = (q.parent / proto["inputs"]["baseline_view"]["file"]).read_bytes()
    baseline = json.loads(gzip.decompress(baseline_raw))
    if baseline.get("schema_version") != 2:
        raise ValueError("Continuation baseline is not schema-v2")
    records = json.loads((work / "plan.json").read_bytes())
    if digest(json_bytes(records)) != proto["private_plan_sha256"]:
        raise ValueError("Private continuation plan changed")
    by_id = {record["pilot_id"]: record for record in records}
    cp = json.loads(gzip.decompress((output / "checkpoint.json.gz").read_bytes()))
    if cp["protocol_sha256"] != digest(q.read_bytes()) or not set(cp["entries"]) <= set(by_id):
        raise ValueError("Continuation checkpoint mismatch")
    entries = cp["entries"]
    checks = []
    for source_id, entry in entries.items():
        record = by_id[source_id]
        for field in ("address_sha256", "payment_txid_sha256", "cutoff_height", "cutoff_block_hash"):
            if entry[field] != record[field]:
                raise ValueError("Frozen source identity changed")
        raw = (work / entry["raw_file"]).read_bytes()
        if digest(raw) != entry["raw_sha256"]:
            raise ValueError("Raw continuation fingerprint mismatch")
        data = json.loads(gzip.decompress(raw))
        if data["address"] != record["address"]:
            raise ValueError("Raw continuation address mismatch")
        regenerated = tail.tail_check(record, data["anchor"], data["transactions"],
            data["pagination_exhausted"], data["anchor_after"], data["parent_statuses"])
        if any(regenerated[field] != entry[field] for field in ("status", "features", "prefix")):
            raise ValueError("Continuation re-extraction differs")
        if (entry["status"] == "complete_prior_prefix" and
                prior_audit.independent_features(record, data) != entry["features"]):
            raise ValueError("Independent continuation recount differs")
        checks.append({"source_id": source_id, "status": entry["status"],
            "pages_fetched": entry["pages_fetched"],
            "pagination_exhausted": data["pagination_exhausted"]})
    requests = json.loads(gzip.decompress((output / "request_manifest.json.gz").read_bytes()))
    responses = 0
    for meta in requests:
        body = work / "requests" / meta["source_id"] / (meta["key"] + ".json.gz")
        if "sha256" in meta:
            if digest(body.read_bytes()) != meta["sha256"]:
                raise ValueError("Continuation response fingerprint mismatch")
            responses += 1
    view = deepcopy(baseline)
    old_by_id = {row["source_id"]: deepcopy(row) for row in baseline["rows"]}
    for row in view["rows"]:
        old = old_by_id[row["source_id"]]
        entry = entries.get(row["source_id"])
        if entry:
            if old["precutoff_history_status"] != "not_completed" or old["features"] is not None:
                raise ValueError("Finished predictor row selected again")
            row["precutoff_history_status"] = entry["status"]
            row["precutoff_history_provenance"] = {
                "pass_name": proto["pass_name"], "raw_sha256": entry["raw_sha256"],
                "full_current_history_counter_coverage_verified": False}
            if entry["status"] == "complete_prior_prefix":
                row["features"] = deepcopy(entry["features"])
        if (row["labels"] != old["labels"] or row["cutoff_height"] != old["cutoff_height"] or
                row["full_history_status"] != old["full_history_status"] or
                row["full_history_provenance"] != old["full_history_provenance"]):
            raise ValueError("Label, cutoff or full-history evidence changed")
        if not entry and row != old:
            raise ValueError("Unselected schema-v2 row changed")
    if len(view["rows"]) != 1500 or len({row["address_sha256"] for row in view["rows"]}) != 1500:
        raise ValueError("Cohort membership changed")
    for source_id, old in old_by_id.items():
        if old["features"] is not None and next(r for r in view["rows"] if r["source_id"] == source_id)["features"] != old["features"]:
            raise ValueError("Existing predictor vector changed")
    view["inputs"].update(reference_tail_continuation_protocol_sha256=digest(q.read_bytes()),
        reference_tail_continuation_checkpoint_sha256=digest((output / "checkpoint.json.gz").read_bytes()),
        predecessor_schema_v2_sha256=digest(baseline_raw))
    raw_view = gzip.compress(json_bytes(view), mtime=0)
    atomic_write(output / "precutoff_feature_view.json.gz", raw_view)
    comparisons = [row for row in view["rows"] if row["known_coldcard_core_membership"] == 0]
    complete_new = sum(entry["status"] == "complete_prior_prefix" for entry in entries.values())
    summary = {
        "schema_version": 2, "verified_at": datetime.now(timezone.utc).isoformat(),
        "selected_sources": 1500, "case_predictors_available": 500,
        "full_history_comparison_statuses": dict(Counter(row["full_history_status"] for row in comparisons)),
        "new_complete_pre_cutoff_comparisons": complete_new,
        "comparison_predictors_available": sum(row["features"] is not None for row in comparisons),
        "comparison_predictors_unavailable": sum(row["features"] is None for row in comparisons),
        "complete_predictor_rows": sum(row["features"] is not None for row in view["rows"]),
        "targeted_sources": len(records), "targeted_results": len(entries),
        "targeted_pending": len(records) - len(entries),
        "targeted_statuses": dict(Counter(entry["status"] for entry in entries.values())),
        "raw_tails_reextracted": len(checks), "independent_new_vectors_checked": complete_new,
        "saved_response_fingerprints_verified": responses,
        "failed_requests": [meta for meta in requests if "error_type" in meta],
        "predecessor_predictor_vectors_preserved": sum(row["features"] is not None for row in baseline["rows"]),
        "all_predecessor_vectors_unchanged": True,
        "labels_and_cutoff_unchanged": True, "feature_count": 14,
        "full_history_status_not_promoted": True, "training_performed": False,
        "split_created": False, "precutoff_view_sha256": digest(raw_view),
        "per_source": checks,
        "limitations": [
            "Reference-tail completeness relies on the original provider indexed-history contract.",
            "A complete prior prefix is not full-current-history counter reconciliation or cryptographic inclusion proof.",
            "A bounded-incomplete prefix has no vector; unknown labels remain unknown."]}
    atomic_write(output / "coverage_audit.json", json_bytes(summary))
    atomic_write(output / "coverage_summary.json", json_bytes(summary))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("work", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.protocol, args.output, args.work)))

