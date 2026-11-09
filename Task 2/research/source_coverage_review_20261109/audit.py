"""Recount the pinned source-prefix coverage offline; never request provider data."""

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path


BASE_COMMIT = "04aae8dd928241fc422fb9bf47e5fae3f1c20bd9"
INPUTS = {
    "coldcard": {
        "directory": "Task 2/research/coldcard/reference_tail_continuation_20261102_1508",
        "sha256": "a96aac7555150122e08dfab2a5d70773df31a28869a52f91cc75a5e12ebe29ab",
        "target": "known_coldcard_core_membership",
        "resume_gap_key": "excluded_bounded_incomplete_source_ids",
        "selected": 1500,
    },
    "cryptobilis": {
        "directory": "Task 2/research/external_cases/cryptobilis_reference_prefix_20261104_201345",
        "sha256": "1e5ddf726ae40caffd9ebcb8113f748dace0a6b6c5df708d80cf1686371eb87e",
        "target": "cryptobilis_reference_source_membership",
        "resume_gap_key": "bounded_incomplete_source_ids",
        "selected": 366,
    },
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_inventory(root):
    result = {
        "schema_version": 1,
        "review_date": "2026-11-09",
        "input_commit": BASE_COMMIT,
        "purpose": "Coverage inventory after Hugo reported Ivan's new research direction",
        "provider_requests": 0,
        "model_fits": 0,
        "new_scores": 0,
        "old_artifacts_modified": False,
        "datasets": {},
    }
    address_sets = []
    expected_allowlist = None
    for name, config in INPUTS.items():
        directory = root / config["directory"]
        view_path = directory / "precutoff_feature_view.json.gz"
        raw = view_path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(digest == config["sha256"], f"Pinned view fingerprint mismatch: {name}")
        view = json.loads(gzip.decompress(raw))
        resume_path = directory / "resume_checkpoint.json"
        resume = read_json(resume_path)
        rows = view["rows"]
        allowlist = view["predictor_allowlist"]
        require(view["schema_version"] == 2, f"Unexpected view schema: {name}")
        require(len(allowlist) == len(set(allowlist)) == 14, f"Feature allowlist: {name}")
        if expected_allowlist is None:
            expected_allowlist = allowlist
        require(allowlist == expected_allowlist, "Feature definitions/ordering differ")
        require(len(rows) == config["selected"], f"Selected population mismatch: {name}")
        require(len({r["source_id"] for r in rows}) == len(rows), f"Duplicate source: {name}")
        addresses = {r["address_sha256"] for r in rows}
        require(len(addresses) == len(rows), f"Duplicate address: {name}")
        address_sets.append(addresses)
        complete = []
        bounded = []
        label_keys = ["independently_verified_compromise", "hardware_signing_at_event", "independently_verified_seed_origin"]
        for row in rows:
            features = row.get("features")
            require(row[config["target"]] in (0, 1), f"Unexpected operational label: {name}")
            require(all(row["labels"].get(k) is None for k in label_keys), f"Verified-label promotion: {name}")
            if features is None:
                require(row["precutoff_history_status"] == "bounded_incomplete", f"Unclassified missing vector: {name}")
                bounded.append(row)
            else:
                require(isinstance(features, dict) and set(features) == set(allowlist), f"Partial feature vector: {name}")
                require(row["precutoff_history_status"] in ("complete_prior_prefix", "complete_full_history"), f"Incomplete prefix with vector: {name}")
                complete.append(row)
        gap_ids = sorted(r["source_id"] for r in bounded)
        require(gap_ids == sorted(resume[config["resume_gap_key"]]), f"Resume/gap inventory mismatch: {name}")
        require(resume["network_source_ids"] == [], f"Old network continuation not closed: {name}")
        result["datasets"][name] = {
            "view": str(view_path.relative_to(root)),
            "view_sha256": digest,
            "resume": str(resume_path.relative_to(root)),
            "resume_sha256": hashlib.sha256(resume_path.read_bytes()).hexdigest(),
            "selected": len(rows),
            "selected_by_operational_class": dict(sorted(Counter("case" if r[config["target"]] else "comparison" for r in rows).items())),
            "available_vectors": len(complete),
            "available_by_operational_class": dict(sorted(Counter("case" if r[config["target"]] else "comparison" for r in complete).items())),
            "bounded_incomplete": len(bounded),
            "bounded_incomplete_source_ids": gap_ids,
            "old_continuation_network_source_ids": [],
            "precutoff_statuses": dict(sorted(Counter(r["precutoff_history_status"] for r in rows).items())),
            "full_current_history_statuses": dict(sorted(Counter(r["full_history_status"] for r in rows).items())),
            "verified_device_compromise_seed_labels": "unknown for all selected rows",
        }
    result["predictor_allowlist"] = expected_allowlist
    result["totals"] = {
        k: sum(x[k] for x in result["datasets"].values())
        for k in ["selected", "available_vectors", "bounded_incomplete"]
    }
    result["cross_dataset_exact_address_overlap"] = len(address_sets[0] & address_sets[1])
    overlap_path = root / "Task 2/research/external_cases/cryptobilis_overlap_20261104_205032/summary.json"
    overlap = read_json(overlap_path)
    result["preserved_overlap_audit"] = {
        "path": str(overlap_path.relative_to(root)),
        "sha256": hashlib.sha256(overlap_path.read_bytes()).hexdigest(),
        "cross_development_components": overlap["cross_development_components"],
        "cryptobilis_quarantined_complete_vectors": overlap["quarantined_complete_external"],
        "cryptobilis_eligible_for_original_frozen_test": overlap["eligible_external"],
        "entity_independence_established": overlap["entity_independence_established"],
    }
    policy_path = root / "Task 2/research/coldcard/comparison_access_retries_20261030/retry_policy.json"
    policy = read_json(policy_path)
    require(policy["collector_lease"]["state"] == "idle", "Published collector lease is not idle")
    require(policy["automation_confirmed_enabled"] is False, "Historical collector automation is enabled")
    result["collection_state_at_input_commit"] = {
        "policy": str(policy_path.relative_to(root)),
        "sha256": hashlib.sha256(policy_path.read_bytes()).hexdigest(),
        "collector_lease": "idle",
        "automation_enabled": False,
        "coverage_extension_started": False,
    }
    result["interpretation"] = [
        "159 unavailable prefixes require new coverage work, not a retry of the exhausted network continuation.",
        "These selected records must be retained without replacement or manufactured vectors.",
        "Prefix completeness and complete current-history coverage are separate measures.",
        "54 complete CryptoBilis vectors are an overlap exclusion, not an acquisition failure.",
        "This audit verifies public export structure, counts and pins; it does not reconstruct private raw histories or revalidate every numerical feature.",
    ]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    require(bool(args.output) != bool(args.check), "Choose exactly one of --output or --check")
    result = build_inventory(args.repo_root.resolve())
    if args.check:
        require(read_json(args.check) == result, "Saved inventory does not reproduce")
    else:
        require(not args.output.exists(), "Refusing to overwrite an existing inventory")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["totals"], sort_keys=True))


if __name__ == "__main__":
    main()
