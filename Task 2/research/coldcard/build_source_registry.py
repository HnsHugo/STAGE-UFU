"""Build a source-address evidence registry, without inferring theft/device labels.

Reuses the pinned Esplora collector history and its existing counter/outpoint
checks. Output addresses and input evidence are regenerated locally, not posted
as a new list of victims. No network access, fitting or external-model changes.
"""
import argparse
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re

from analyze_case_flows import reconcile_received_prevouts, span, utc
from collect_theft_seeds import check_history

HEX64 = re.compile(r"[0-9a-f]{64}")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def sat(value):
    if type(value) is not int or value < 0:
        raise ValueError("Expected nonnegative integer satoshis")
    return value


def timestamp(value):
    date = datetime.fromisoformat(value)
    if date.tzinfo is None:
        raise ValueError("Window dates require an explicit timezone")
    return date.timestamp()


def validate_outpoint(item):
    txid, index = item.get("txid"), item.get("vout")
    if not isinstance(txid, str) or not HEX64.fullmatch(txid):
        raise ValueError("Missing or invalid previous TXID")
    if type(index) is not int or not 0 <= index < 2**32:
        raise ValueError("Missing or invalid previous output index")
    return txid, index


def build(history, protocol):
    collector = protocol["collector_address"]
    if history["address"] != collector:
        raise ValueError("Collector/history address mismatch")
    if not history.get("provider") or not history.get("collected_at"):
        raise ValueError("Provider and collection time are required")
    for key in ("before", "after"):
        if history[key].get("address") != collector:
            raise ValueError("Provider-counter address mismatch")
    audit = check_history(collector, history["transactions"], history["before"],
                          history["after"], history["audit"]["pagination_exhausted"])
    if not audit["coverage_complete_by_provider_counters"]:
        raise ValueError("Stable complete collector history required")
    start = timestamp(protocol["candidate_window"]["start_utc"])
    end = timestamp(protocol["candidate_window"]["end_exclusive_utc"])
    if start >= end:
        raise ValueError("Empty or reversed candidate interval")
    if protocol.get("address_specific_compromise_evidence") or protocol.get("address_specific_hardware_evidence"):
        raise ValueError("This graph-only extractor does not ingest supervised labels")

    # A consumed collector output must match its actual received output in the
    # saved history. Upstream source outputs are provider assertions, not fetched
    # independently by this script.
    spent_check = reconcile_received_prevouts(history["transactions"], collector)
    spent_by, used = {}, set()
    for tx in history["transactions"]:
        if not HEX64.fullmatch(tx["txid"]):
            raise ValueError("Invalid payment TXID")
        for item in tx["vin"]:
            if item.get("is_coinbase", False):
                continue
            key = validate_outpoint(item)
            if key in used:
                raise ValueError("Duplicate spent outpoint in collector history")
            used.add(key)
            previous = item.get("prevout") or {}
            if previous.get("scriptpubkey_address") == collector:
                spent_by[key] = tx["txid"]

    groups = {name: dict(receipts=0, received_sat=0, input_slots=0,
                        input_value_sat=0, fees_sat=0, missing_prevouts=0,
                        missing_input_addresses=0, coinbase_inputs=0,
                        self_input_slots=0, value_unreconciled_transactions=0,
                        multi_source_address_transactions=0,
                        received_outputs_later_consumed=0,
                        unique_sources=set(), times=[], inputs_per_transaction=Counter(),
                        outputs_per_transaction=Counter())
              for name in ("candidate_window", "outside_candidate_window")}
    addresses, observations = {}, []
    for tx in sorted(history["transactions"], key=lambda t: (t["status"]["block_time"], t["txid"])):
        matching = [(n, o) for n, o in enumerate(tx["vout"])
                    if o.get("scriptpubkey_address") == collector]
        for out in tx["vout"]:
            sat(out["value"])
        if not matching:
            continue
        when = tx["status"]["block_time"]
        scope = "candidate_window" if start <= when < end else "outside_candidate_window"
        group = groups[scope]
        group["receipts"] += 1
        group["received_sat"] += sum(sat(o["value"]) for _, o in matching)
        group["fees_sat"] += sat(tx["fee"])
        group["times"].append(when)
        group["inputs_per_transaction"][len(tx["vin"])] += 1
        group["outputs_per_transaction"][len(tx["vout"])] += 1
        distinct = {(i.get("prevout") or {}).get("scriptpubkey_address")
                    for i in tx["vin"]} - {None}
        group["multi_source_address_transactions"] += len(distinct) > 1
        receipts = [dict(txid=tx["txid"], vout=n, value_sat=o["value"],
                         observed_spending_txid=spent_by.get((tx["txid"], n)))
                    for n, o in matching]
        group["received_outputs_later_consumed"] += sum(
            r["observed_spending_txid"] is not None for r in receipts)
        values = []
        for vin, item in enumerate(tx["vin"]):
            if item.get("is_coinbase", False):
                group["coinbase_inputs"] += 1
                continue
            group["input_slots"] += 1
            previous = item.get("prevout") or {}
            address = previous.get("scriptpubkey_address")
            if not previous:
                group["missing_prevouts"] += 1
            if not address:
                group["missing_input_addresses"] += 1
            value = sat(previous["value"]) if "value" in previous else None
            values.append(value)
            if value is not None:
                group["input_value_sat"] += value
            previous_txid, n = validate_outpoint(item)
            observation = dict(
                evidence_id=f"{tx['txid']}:{vin}", source_address=address,
                payment_txid=tx["txid"], payment_vin=vin,
                previous_outpoint=dict(txid=previous_txid, vout=n),
                spent_input_value_sat=value,
                previous_script_type=previous.get("scriptpubkey_type"),
                previous_script_sha256=(digest(bytes.fromhex(previous["scriptpubkey"]))
                                        if "scriptpubkey" in previous else None),
                confirmed_utc=utc(when), block_height=tx["status"]["block_height"],
                block_hash=tx["status"]["block_hash"], scope=scope,
                collector_receipts=receipts,
                provider_url=f"{history['provider'].rstrip('/')}/tx/{tx['txid']}",
                observed_at=history["collected_at"],
                previous_output_verification="Provider prevout record only; upstream transaction not independently retrieved",
                collector_value_allocated_to_this_input_sat=None)
            observations.append(observation)
            if address == collector:
                group["self_input_slots"] += 1
                continue
            if not address:
                continue
            group["unique_sources"].add(address)
            row = addresses.setdefault(address, dict(
                network=protocol["network"], address=address,
                case_id=protocol["case_id"], split_group=protocol["case_id"],
                entity_id=None, observed_role="input_address_of_collector_payment",
                case_relation="graph_candidate", relation_confidence="observed_in_provider_records",
                compromise_status="unknown", compromise_confidence="unknown",
                compromise_evidence=[], hardware_control="unknown", hardware_confidence="unknown",
                hardware_evidence=[], supervised_compromise_label=None,
                supervised_hardware_label=None, label_available_at=None,
                relation_observed_at=history["collected_at"], reviewed_on=protocol["reviewed_on"],
                source_address_history_complete=False, all_wallet_utxos_drained="unknown",
                source_context="Case-context URLs in protocol do not provide per-address victim/device evidence",
                evidence_ids=[], scopes=set(), times=[], payment_txids=set(),
                known_spent_input_value_sat=0, inputs_with_unknown_value=0))
            row["evidence_ids"].append(observation["evidence_id"])
            row["scopes"].add(scope)
            row["times"].append(when)
            row["payment_txids"].add(tx["txid"])
            if value is None:
                row["inputs_with_unknown_value"] += 1
            else:
                row["known_spent_input_value_sat"] += value
        if len(values) == len(tx["vin"]) and all(v is not None for v in values):
            if sum(values) != sum(o["value"] for o in tx["vout"]) + tx["fee"]:
                raise ValueError("Payment input/output/fee mismatch")
        else:
            group["value_unreconciled_transactions"] += 1

    rows = []
    for address in sorted(addresses):
        row = addresses[address]
        row["observed_confirmation_span"] = span(row.pop("times"))
        row["scopes"] = sorted(row["scopes"])
        row["payment_txids"] = sorted(row["payment_txids"])
        row["evidence_ids"].sort()
        row["distinct_payment_count"] = len(row["payment_txids"])
        row["spent_previous_output_count"] = len(row["evidence_ids"])
        rows.append(row)
    overlap = groups["candidate_window"]["unique_sources"] & groups["outside_candidate_window"]["unique_sources"]
    for group in groups.values():
        group["distinct_source_addresses"] = len(group.pop("unique_sources"))
        group["receipt_confirmation_span"] = span(group.pop("times"))
        for field in ("inputs_per_transaction", "outputs_per_transaction"):
            group[field] = dict(sorted(group[field].items()))
    summary = dict(
        schema_version=1, case_id=protocol["case_id"], status="executed_graph_evidence_registry",
        observation_unit="Source address, linked to each observed payment input and previous outpoint",
        history_collected_at=history["collected_at"], reviewed_on=protocol["reviewed_on"],
        history_audit=audit, collector_spent_output_reconciliation=spent_check,
        groups=groups, source_address_count=len(rows), input_evidence_count=len(observations),
        source_addresses_shared_across_windows=len(overlap), incident_group_count=1,
        verified_compromised_source_labels=0, verified_hardware_source_labels=0,
        supervised_training_ready=False, model_training_performed=False,
        blockers=["No address-specific verified compromise or hardware labels in supplied evidence",
                  "No documented legitimate control cohort or independent incident split",
                  "Complete source-address histories and prior-output inclusion not verified"],
        limitations=["Candidate UTC day is not an independently verified exact theft interval",
                     "Input addresses and UTXOs are not people, victims, devices or independent cases",
                     "Spent input sums and gross receipts are not certified stolen amounts",
                     "Later collector spending is retrospective evidence, not a pre-event feature",
                     "Unknown outside-window sources are not legitimate controls",
                     "Counter/outpoint reconciliation is not cryptographic inclusion verification"])
    return rows, observations, summary


def artifacts(protocol_path):
    protocol_path = Path(protocol_path)
    protocol_raw = protocol_path.read_bytes()
    protocol = json.loads(protocol_raw)
    history_path = protocol_path.parent / protocol["history_file"]
    raw = history_path.read_bytes()
    if digest(raw) != protocol["history_sha256"]:
        raise ValueError("Pinned history SHA256 mismatch")
    history = json.loads(gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw)
    rows, observations, summary = build(history, protocol)
    files = {"addresses.json": json_bytes(dict(schema_version=1, records=rows)),
             "input_evidence.jsonl": b"".join(
                 (json.dumps(row, sort_keys=True) + "\n").encode() for row in observations)}
    summary["inputs"] = dict(protocol_sha256=digest(protocol_raw),
                             history_sha256=digest(raw), history_file=protocol["history_file"],
                             script_sha256=digest(Path(__file__).read_bytes()))
    summary["generated_local_artifacts"] = {
        name: dict(sha256=digest(value), bytes=len(value)) for name, value in files.items()}
    files["summary.json"] = json_bytes(summary)
    return files, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("protocol", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    files, summary = artifacts(args.protocol)
    if args.command == "build":
        args.output.mkdir(parents=True, exist_ok=False)
        for name, raw in files.items():
            (args.output / name).write_bytes(raw)
    else:
        for name, raw in files.items():
            if (args.output / name).read_bytes() != raw:
                raise ValueError(f"Registry reproduction mismatch: {name}")
    print(json.dumps(dict(command=args.command, source_addresses=summary["source_address_count"],
                          input_evidence=summary["input_evidence_count"],
                          groups=summary["groups"], supervised_training_ready=False), indent=2))


if __name__ == "__main__":
    main()
