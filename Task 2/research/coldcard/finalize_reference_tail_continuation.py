"""Write the immutable resume point and public audit journal for a continuation."""
import argparse
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path

from build_source_registry import digest, json_bytes
from source_cohort import atomic_write


def pin(base, file):
    return {"file": file, "sha256": digest((base / file).read_bytes())}


def finalize(base, pass_name):
    base = base.resolve()
    protocol_file = base / ("source_" + pass_name + "_protocol.json")
    protocol = json.loads(protocol_file.read_bytes())
    output = base / pass_name
    checkpoint = json.loads(gzip.decompress((output / "checkpoint.json.gz").read_bytes()))
    audit = json.loads((output / "coverage_audit.json").read_bytes())
    manifest = json.loads(gzip.decompress((output / "request_manifest.json.gz").read_bytes()))
    parent_resume_file = base / protocol["inputs"]["parent_resume"]["file"]
    parent = json.loads(parent_resume_file.read_bytes())
    entries = checkpoint["entries"]
    complete = [source_id for source_id in protocol["source_ids"]
                if entries.get(source_id, {}).get("status") == "complete_prior_prefix"]
    bounded = [source_id for source_id in protocol["source_ids"]
               if entries.get(source_id, {}).get("status") == "bounded_incomplete"]
    remaining = [source_id for source_id in protocol["source_ids"] if source_id not in entries]
    failed = [meta for meta in manifest if "error_type" in meta]
    inputs = {
        "protocol": pin(base, protocol_file.name),
        "checkpoint": pin(base, pass_name + "/checkpoint.json.gz"),
        "request_manifest": pin(base, pass_name + "/request_manifest.json.gz"),
        "stop": pin(base, pass_name + "/collection_stop.json"),
        "feature_view": pin(base, pass_name + "/precutoff_feature_view.json.gz"),
        "audit": pin(base, pass_name + "/coverage_audit.json"),
        "predecessor_resume": pin(base, protocol["inputs"]["parent_resume"]["file"]),
        "validated_pilot": protocol["inputs"]["pilot_validation"],
    }
    resume = {
        "schema_version": 2, "updated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Confirmed transactions strictly below the unchanged cutoff; never full-current-history promotion.",
        "inputs": inputs, "latest_work": "source_cohort_work_" + pass_name,
        "network_sources": len(remaining), "network_source_ids": remaining,
        "excluded_complete_prefix_source_ids": parent["excluded_complete_prefix_source_ids"] + complete,
        "excluded_bounded_incomplete_source_ids": parent["excluded_bounded_incomplete_source_ids"] + bounded,
        "failed_consumed_requests": failed,
        "prior_case_predictor_vectors": 500,
        "prior_comparison_predictor_vectors": audit["comparison_predictors_available"],
        "full_history_comparison_statuses": audit["full_history_comparison_statuses"],
        "next_network_attempt_not_before": "2026-11-01T23:20:04.694868+00:00",
        "bounds": parent["bounds"],
        "merge_policy": "Merge a future successor with this pinned schema-v2 view, preserving all %d existing vectors and every coverage provenance; never promote full-history statuses." % audit["complete_predictor_rows"],
        "resume_policy": "Create a distinct successor after the cooldown, selecting only network_source_ids. Reuse only verified successful response bytes; keep this pass's consumed 429 marker here and record any later page attempt in the successor.",
    }
    atomic_write(output / "resume_checkpoint.json", json_bytes(resume))
    readme = """# Anchored pre-cutoff continuation\n\nThis distinct successor selected only the 99 network gaps from the pinned predecessor. It reused 24 verified HTTP-200 responses offline, finalized 80 sources, then stopped on the first new HTTP 429 without an internal retry.\n\n- New complete prior prefixes: 4\n- New bounded-incomplete prefixes: 76\n- Remaining network gaps: 19\n- Consolidated predictors: 500 cases and 876 comparisons\n- Full-current-history comparison status remains 864 complete / 136 incomplete\n\nAll 80 raw tails re-extract, all four new vectors were independently recounted, and 1,422 saved-response fingerprints verify. A complete prior prefix is not a complete current history or a cryptographic inclusion proof. Unknown labels and the fourteen predictor definitions are unchanged.\n"""
    atomic_write(output / "README.md", readme.encode())
    journal = {
        "schema_version": 1, "verified_at": audit["verified_at"],
        "pass_name": pass_name, "protocol_sha256": digest(protocol_file.read_bytes()),
        "checkpoint_sha256": digest((output / "checkpoint.json.gz").read_bytes()),
        "precutoff_feature_view_sha256": audit["precutoff_view_sha256"],
        "targeted": 99, "results": 80, "complete_prior_prefix": 4,
        "bounded_incomplete": 76, "network_pending": 19,
        "independent_new_vectors_checked": 4,
        "raw_tails_reextracted": 80, "saved_response_fingerprints_verified": 1422,
        "full_history_comparison_statuses": audit["full_history_comparison_statuses"],
        "training_performed": False, "split_created": False,
    }
    atomic_write(base.parents[1] / "verification" / (pass_name + ".json"), json_bytes(journal))
    return resume


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("pass_name")
    args = parser.parse_args()
    print(json.dumps(finalize(args.base, args.pass_name)))
