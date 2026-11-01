"""Prepare a pinned successor for an interrupted anchored reference-tail pass."""
import argparse
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import shutil

from build_source_registry import digest, json_bytes
from source_cohort import atomic_write


def pin(base, file):
    return {"file": file, "sha256": digest((base / file).read_bytes())}


def copy_verified_prefix(parent_work, work, record):
    source = parent_work / "requests" / record["pilot_id"]
    target = work / "requests" / record["pilot_id"]
    if not source.exists():
        return 0
    copied = 0
    reference = source / "reference.json"
    if reference.exists():
        meta = json.loads(reference.read_bytes())
        body = source / "reference.json.gz"
        expected = "/tx/" + record["payment_txid"]
        if (meta.get("http_status") != 200 or not body.exists() or
                digest(body.read_bytes()) != meta.get("sha256") or
                digest(expected.encode()) != meta.get("endpoint_sha256")):
            raise ValueError("Invalid cached reference response")
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(reference, target / reference.name)
        shutil.copy2(body, target / body.name)
        copied += 1
    cursor = record["payment_txid"]
    for index in range(16):
        key = "tail_%04d" % index
        marker, body = source / (key + ".json"), source / (key + ".json.gz")
        if not body.exists():
            break
        meta = json.loads(marker.read_bytes())
        expected = "/address/%s/txs/chain/%s" % (record["address"], cursor)
        raw = body.read_bytes()
        if (meta.get("http_status") != 200 or digest(raw) != meta.get("sha256") or
                digest(expected.encode()) != meta.get("endpoint_sha256")):
            raise ValueError("Invalid cached cursor response")
        page = json.loads(gzip.decompress(raw))
        if not isinstance(page, list) or len(page) > 25:
            raise ValueError("Invalid cached cursor page")
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(marker, target / marker.name)
        shutil.copy2(body, target / body.name)
        copied += 1
        if not page:
            break
        cursor = page[-1]["txid"]
    return copied


def prepare(base, pass_name, access_response_sha256, access_tx_count):
    parent_output = base / "reference_tail_coverage_20261031_221432"
    parent_work = base / "source_cohort_work_reference_tail_coverage_20261031_221432"
    resume_file = parent_output / "resume_checkpoint.json"
    resume = json.loads(resume_file.read_bytes())
    for value in resume["inputs"].values():
        if digest((base / value["file"]).read_bytes()) != value["sha256"]:
            raise ValueError("Pinned parent input changed")
    parent_plan = json.loads((parent_work / "plan.json").read_bytes())
    by_id = {record["pilot_id"]: record for record in parent_plan}
    ids = resume["network_source_ids"]
    if len(ids) != resume["network_sources"] or len(ids) != len(set(ids)):
        raise ValueError("Invalid parent network selection")
    if set(ids) & (set(resume["excluded_complete_prefix_source_ids"]) |
                   set(resume["excluded_bounded_incomplete_source_ids"])):
        raise ValueError("Finished parent result selected again")
    plan = [by_id[source_id] for source_id in ids]
    output = base / pass_name
    work = base / ("source_cohort_work_" + pass_name)
    output.mkdir(parents=True, exist_ok=False)
    work.mkdir(parents=True, exist_ok=False)
    atomic_write(work / "plan.json", json_bytes(plan))
    copied = sum(copy_verified_prefix(parent_work, work, record) for record in plan)
    inputs = {
        "parent_resume": pin(base, "reference_tail_coverage_20261031_221432/resume_checkpoint.json"),
        "parent_protocol": resume["inputs"]["protocol"],
        "parent_checkpoint": resume["inputs"]["checkpoint"],
        "parent_request_manifest": resume["inputs"]["request_manifest"],
        "parent_stop": resume["inputs"]["stop"],
        "baseline_view": resume["inputs"]["feature_view"],
        "parent_audit": resume["inputs"]["audit"],
        "pilot_validation": resume["inputs"]["validated_pilot"],
        "collector": pin(base, "collect_reference_tail.py"),
        "batch_runner": pin(base, "collect_reference_tail_many.py"),
        "ledger": pin(base, "collect_comparison_coverage.py"),
        "transport": pin(base, "comparison_http.py"),
        "feature_extractor": pin(base, "prepayment_pilot.py"),
        "continuation_auditor": pin(base, "audit_reference_tail_continuation.py"),
    }
    protocol = {
        "schema_version": 1,
        "pass_name": pass_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "authorization": "User-authorized anchored pre-cutoff continuation after the saved cooldown.",
        "provider": "https://blockstream.info/api",
        "coverage_scope": "Exhausted confirmed prefix strictly below the frozen cutoff; never full-current-history promotion.",
        "failure_policy": "Stop on first 403/429 or other request failure; no internal retry, provider, route, account, proxy, IP or TLS change.",
        "merge_policy": resume["merge_policy"],
        "inputs": inputs,
        "source_ids": ids,
        "private_plan_sha256": digest(json_bytes(plan)),
        "reused_successful_responses": copied,
        "parent_failed_markers_reused": False,
        "normal_counter_access_check": {
            "source_id": ids[0],
            "performed_before_successor_collection": True,
            "http_status": 200,
            "response_sha256": access_response_sha256,
            "observed_full_transaction_count": access_tx_count,
            "repeat_inside_successor": False,
        },
        "batch_size": 20,
        "max_batches": 5,
        "workers": 2,
        "requests_per_second": 1,
        "max_pages_per_address": 16,
        "timeout_seconds": 15,
        "labels": "Unknown labels, the fourteen definitions and every strict cutoff are unchanged.",
    }
    protocol_file = base / ("source_" + pass_name + "_protocol.json")
    atomic_write(protocol_file, json_bytes(protocol))
    redacted = [{k: record[k] for k in ("pilot_id", "address_sha256", "payment_txid_sha256", "cutoff_height", "cutoff_block_hash")}
                for record in plan]
    atomic_write(output / "plan.json.gz", gzip.compress(json_bytes(redacted), mtime=0))
    atomic_write(output / "access_check.json", json_bytes(protocol["normal_counter_access_check"]))
    return protocol_file, output, work, copied


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("pass_name")
    parser.add_argument("access_response_sha256")
    parser.add_argument("access_tx_count", type=int)
    args = parser.parse_args()
    print(prepare(args.base, args.pass_name, args.access_response_sha256, args.access_tx_count))
