"""Audit saved pilot independence; never fit, tune, or predict a model.

The source transaction identifiers are only four extrema per address, so a
non-match is not proof of full-history disjointness. Co-addresses mean decoded
addresses in the same transaction, including change and batched recipients;
they are not identified owners or necessarily direct economic counterparties.
"""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
import platform
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median


TX_COLUMNS = (
    "max_sent_transaction_id", "min_sent_transaction_id",
    "max_received_transaction_id", "min_received_transaction_id",
)
FIXED_MODEL = dict(n_estimators=100, max_depth=20, min_samples_leaf=20,
                   max_features="sqrt", class_weight=1, random_state=42,
                   threshold=0.15)
COUNTERS = ("tx_count", "funded_txo_count", "spent_txo_count",
            "funded_txo_sum", "spent_txo_sum")


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read_json(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def evidence_group(record):
    """Keep attribution groups even when transaction histories are disjoint."""
    group = record.get("case_group") or record.get("entity_group")
    if not group:
        raise ValueError("Missing explicit evidence group")
    return str(group).lower()


def satoshis(output):
    value = output.get("value")
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("Expected a nonnegative integer satoshi amount")
    return value


def verify_history(path, row):
    """Verify bytes, focal identity, and confirmed provider-counter coverage."""
    if sha256(path) != row["history_sha256"]:
        raise ValueError(f"History SHA256 mismatch: {path}")
    history = read_json(path)
    address = row["address"]
    if history["address"] != address:
        raise ValueError("Score/history address mismatch")
    source = history.get("source_record", history.get("record"))
    if source != row["source_record"] or source.get("address") != address:
        raise ValueError("Score/history source-record mismatch")
    if history["collected_at"] != row["collected_at"]:
        raise ValueError("Score/history collection-time mismatch")
    if history["audit"].get("pagination_exhausted") is not True:
        raise ValueError("Unfinished history pagination")
    if history["audit"].get("coverage_complete_by_provider_counters") is not True:
        raise ValueError("Saved history does not claim reconciled coverage")
    score = row["source_category_score"]
    if not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError("Invalid saved score")
    if row["threshold"] != FIXED_MODEL["threshold"]:
        raise ValueError("Threshold differs from frozen pilot")
    if row["above_fixed_threshold"] is not (score > row["threshold"]):
        raise ValueError("Saved alert disagrees with strict threshold")

    observed = dict.fromkeys(COUNTERS, 0)
    transactions = {}
    coaddresses = set()
    coinbase_count = missing_input_address = missing_output_address = 0
    for tx in history["transactions"]:
        txid = tx["txid"]
        if txid in transactions:
            raise ValueError("Duplicate transaction in one saved history")
        if tx.get("status", {}).get("confirmed") is not True:
            raise ValueError("Unconfirmed transaction in full-history pilot")
        transactions[txid] = tx
        focal_input = focal_output = False
        for vin in tx["vin"]:
            if vin.get("is_coinbase"):
                if vin.get("prevout") is not None:
                    raise ValueError("Coinbase input unexpectedly has prevout")
                coinbase_count += 1
                continue
            prevout = vin.get("prevout")
            if not isinstance(prevout, dict):
                raise ValueError("Missing non-coinbase prevout")
            value = satoshis(prevout)
            participant = prevout.get("scriptpubkey_address")
            if participant:
                coaddresses.add(participant)
            else:
                missing_input_address += 1
            if participant == address:
                focal_input = True
                observed["spent_txo_count"] += 1
                observed["spent_txo_sum"] += value
        for output in tx["vout"]:
            value = satoshis(output)
            participant = output.get("scriptpubkey_address")
            if participant:
                coaddresses.add(participant)
            else:
                missing_output_address += 1
            if participant == address:
                focal_output = True
                observed["funded_txo_count"] += 1
                observed["funded_txo_sum"] += value
        if not (focal_input or focal_output):
            raise ValueError("Unrelated transaction in focal address history")
        observed["tx_count"] += 1
    coaddresses.discard(address)
    for side in ("before", "after"):
        if history[side].get("address") != address:
            raise ValueError("Provider-counter address mismatch")
        expected = {k: history[side]["chain_stats"][k] for k in COUNTERS}
        if observed != expected:
            raise ValueError(f"Provider-counter reconciliation failed: {side}")
    if observed != {k: history["audit"]["observed"][k] for k in COUNTERS}:
        raise ValueError("Saved audit counters disagree with recomputation")
    return dict(address=address, evidence_group=evidence_group(source),
                source_record=source, history_file=path.name,
                history_sha256=row["history_sha256"],
                collected_at=history["collected_at"], provider=history.get("provider"),
                recomputed_provider_counters=observed,
                coinbase_inputs=coinbase_count,
                inputs_without_decoded_address=missing_input_address,
                outputs_without_decoded_address=missing_output_address,
                decoded_coaddress_count=len(coaddresses),
                source_category_score=score,
                above_fixed_threshold=row["above_fixed_threshold"],
                outside_training_minmax=row.get("outside_training_minmax", []),
                _transactions=transactions, _coaddresses=coaddresses)


def pairwise_overlap(profiles):
    def economic_signature(tx):
        inputs = [(v.get("is_coinbase", False), v.get("txid"), v.get("vout"),
                   (v.get("prevout") or {}).get("value"),
                   (v.get("prevout") or {}).get("scriptpubkey_address")) for v in tx["vin"]]
        outputs = [(satoshis(v), v.get("scriptpubkey_address")) for v in tx["vout"]]
        return inputs, outputs

    pairs = []
    dependencies = []
    owners = defaultdict(set)
    transactions = {}
    for profile in profiles:
        for txid, tx in profile["_transactions"].items():
            owners[txid].add(profile["address"])
            if txid in transactions:
                # Compare economic fields; normalization can omit witness/asm.
                if economic_signature(transactions[txid]) != economic_signature(tx):
                    raise ValueError("Conflicting shared transaction economic fields")
            transactions[txid] = tx
    for a, b in itertools.combinations(profiles, 2):
        common_tx = sorted(a["_transactions"].keys() & b["_transactions"].keys())
        common_addresses = sorted(a["_coaddresses"] & b["_coaddresses"])
        pairs.append(dict(address_a=a["address"], address_b=b["address"],
                          same_evidence_group=a["evidence_group"] == b["evidence_group"],
                          shared_transaction_count=len(common_tx), shared_txids=common_tx,
                          shared_coaddress_count=len(common_addresses),
                          shared_coaddresses=common_addresses,
                          focal_a_in_b_coaddresses=a["address"] in b["_coaddresses"],
                          focal_b_in_a_coaddresses=b["address"] in a["_coaddresses"]))
    for child_id, child in sorted(transactions.items()):
        for input_index, vin in enumerate(child["vin"]):
            parent_id = vin.get("txid")
            if vin.get("is_coinbase") or parent_id not in transactions:
                continue
            cross_pairs = sorted((a, b) for a in owners[parent_id]
                                 for b in owners[child_id] if a != b)
            if not cross_pairs:
                continue
            index = vin["vout"]
            if not isinstance(index, int) or not 0 <= index < len(transactions[parent_id]["vout"]):
                raise ValueError("Invalid cross-history parent output index")
            actual = transactions[parent_id]["vout"][index]
            previous = vin["prevout"]
            if (satoshis(actual), actual.get("scriptpubkey_address")) != (
                    satoshis(previous), previous.get("scriptpubkey_address")):
                raise ValueError("Cross-history outpoint value/address mismatch")
            dependencies.append(dict(parent_txid=parent_id, parent_output=index,
                                     child_txid=child_id, child_input=input_index,
                                     value_sat=satoshis(actual),
                                     spending_address=actual.get("scriptpubkey_address"),
                                     history_pairs=[dict(parent_history=a, child_history=b)
                                                    for a, b in cross_pairs]))
    return pairs, dependencies


def address_roles(tx, address):
    """Describe appearances, without attributing change, ownership or fund flows."""
    inputs = [v["prevout"] for v in tx["vin"] if not v.get("is_coinbase")
              and (v.get("prevout") or {}).get("scriptpubkey_address") == address]
    outputs = [v for v in tx["vout"] if v.get("scriptpubkey_address") == address]
    return dict(input_count=len(inputs), input_value_sat=sum(map(satoshis, inputs)),
                output_count=len(outputs), output_value_sat=sum(map(satoshis, outputs)))


def source_overlap(profiles, source_rows, membership):
    """Use address and extrema identifiers, not numerical prediction features."""
    result = {}
    all_pilot_txids = set().union(*(set(p["_transactions"]) for p in profiles))
    for name, rows in source_rows.items():
        by_address = {row["address"]: row for row in rows}
        if len(by_address) != len(rows):
            raise ValueError(f"Duplicate source address in {name}")
        matching_extrema = defaultdict(list)
        for row in rows:
            for column in TX_COLUMNS:
                txid = row[column]
                if txid in all_pilot_txids:
                    matching_extrema[txid].append(dict(
                        address=row["address"], source_label=row["label"],
                        benchmark_split=membership.get(row["address"], "excluded_from_benchmark"),
                        source_field=column))
        source_result = {}
        for profile in profiles:
            coaddress_matches = []
            for address in sorted(profile["_coaddresses"] & by_address.keys()):
                coaddress_matches.append(dict(address=address, source_label=by_address[address]["label"],
                    benchmark_split=membership.get(address, "excluded_from_benchmark")))
            tx_matches = []
            for txid in sorted(profile["_transactions"].keys() & matching_extrema.keys()):
                tx = profile["_transactions"][txid]
                records = []
                for source_record in matching_extrema[txid]:
                    roles = address_roles(tx, source_record["address"])
                    expected_side = "input_count" if "sent" in source_record["source_field"] else "output_count"
                    records.append(dict(**source_record, observed_roles=roles,
                                        observed_on_expected_side=roles[expected_side] > 0))
                tx_matches.append(dict(txid=txid, input_count=len(tx["vin"]),
                                       output_count=len(tx["vout"]),
                                       focal_observed_roles=address_roles(tx, profile["address"]),
                                       source_records=records))
            source_result[profile["address"]] = dict(
                focal_address_present=profile["address"] in by_address,
                coaddress_match_count=len(coaddress_matches), coaddress_matches=coaddress_matches,
                coaddress_matches_by_split=dict(sorted(Counter(
                    r["benchmark_split"] for r in coaddress_matches).items())),
                extrema_transaction_match_count=len(tx_matches), extrema_transaction_matches=tx_matches,
                matched_source_address_count=len({r["address"] for t in tx_matches for r in t["source_records"]}))
        present_by_column = {c: sum(bool(r[c]) for r in rows) for c in TX_COLUMNS}
        result[name] = dict(source_address_rows=len(rows),
                            source_rows_by_benchmark_split=dict(sorted(Counter(
                                membership.get(r["address"], "excluded_from_benchmark") for r in rows).items())),
                            source_rows_with_any_extrema=sum(any(r[c] for c in TX_COLUMNS) for r in rows),
                            nonempty_extrema_by_column=present_by_column,
                            distinct_nonempty_extrema_txids=len({r[c] for r in rows for c in TX_COLUMNS if r[c]}),
                            profiles=source_result)
    return result


def group_summary(profiles):
    grouped = defaultdict(list)
    for profile in profiles:
        grouped[profile["evidence_group"]].append(profile)
    return [dict(evidence_group=group, addresses=len(rows),
                 above_fixed_threshold=sum(r["above_fixed_threshold"] for r in rows),
                 score_min=min(r["source_category_score"] for r in rows),
                 score_median=median(r["source_category_score"] for r in rows),
                 score_max=max(r["source_category_score"] for r in rows),
                 source_urls=sorted({r["source_record"]["source_url"] for r in rows}),
                 member_addresses=sorted(r["address"] for r in rows))
            for group, rows in sorted(grouped.items())]


def locate_history(row, roots):
    candidates = {p.resolve() for root in roots for p in root.rglob(row["history_file"]) if p.is_file()}
    matches = sorted(p for p in candidates if sha256(p) == row["history_sha256"])
    if not matches:
        raise ValueError(f"No matching saved history bytes found: {row['history_file']}")
    return matches[0]


def run(source, score_paths, history_roots):
    # Imports for split reconstruction only. No estimator is instantiated here.
    import pandas as pd
    import sklearn
    from train_source_categories import HASHES, prepare, split

    reports = [read_json(path) for path in score_paths]
    if not reports:
        raise ValueError("At least one saved score report is required")
    rows = []
    for report in reports:
        if report["source_sha256"] != HASHES or report["fixed_model"] != FIXED_MODEL:
            raise ValueError("Saved report source/model contract mismatch")
        if len(report["base_features"]) != 19 or report["base_features"] != reports[0]["base_features"]:
            raise ValueError("Saved feature contract mismatch")
        rows.extend(report["results"])
    if len({r["address"] for r in rows}) != len(rows):
        raise ValueError("Repeated focal address across score reports")
    if not rows:
        raise ValueError("Saved score reports contain no profiles")
    source_rows = {}
    for name, expected in HASHES.items():
        path = source / name
        if sha256(path) != expected:
            raise ValueError(f"Source SHA256 mismatch: {name}")
        with path.open(encoding="utf-8", newline="") as handle:
            source_rows[name] = [{k: r[k] for k in ("address", "label", "transaction_number", *TX_COLUMNS)}
                                 for r in csv.DictReader(handle, delimiter="\t")]
    frames = []
    for name in ("BB.tsv", "CB.tsv"):
        frame = pd.DataFrame(source_rows[name])[["address", "label", "transaction_number"]]
        frame["transaction_number"] = pd.to_numeric(frame["transaction_number"], errors="raise")
        frames.append(frame)
    data = prepare(*frames)
    train, validation, test = split(data)
    split_indices = dict(train=train, validation=validation, reserved_test=test)
    membership = {data.iloc[i].address: name for name, indices in split_indices.items() for i in indices}
    if any(r["training_addresses"] != len(train) for r in reports):
        raise ValueError("Training membership differs from saved score reports")
    profiles = [verify_history(locate_history(row, history_roots), row) for row in rows]
    pairs, dependencies = pairwise_overlap(profiles)
    overlaps = source_overlap(profiles, source_rows, membership)
    groups = group_summary(profiles)
    return dict(
        status="Executed descriptive independence audit; no independent labeled evaluation established",
        executed_at=datetime.now(timezone.utc).isoformat(),
        operation="Read saved scores and source identity/extrema metadata; no model fitting, retuning or predictions",
        score_reports=[dict(file=p.name, sha256=sha256(p)) for p in score_paths],
        source_sha256=HASHES, audit_script_sha256=sha256(Path(__file__)),
        split_code_sha256=sha256(Path(__file__).with_name("train_source_categories.py")),
        runtime=dict(python=platform.python_version(), pandas=pd.__version__, scikit_learn=sklearn.__version__),
        fixed_model=FIXED_MODEL,
        split_membership_counts={name: len(indices) for name, indices in split_indices.items()},
        split_membership_sha256=hashlib.sha256(json.dumps(membership, sort_keys=True).encode()).hexdigest(),
        scope=dict(addresses=len(profiles), evidence_groups=len(groups),
                   confirmed_transactions_sum=sum(len(p["_transactions"]) for p in profiles),
                   distinct_confirmed_transactions=len(set().union(*(set(p["_transactions"]) for p in profiles))),
                   pairwise_comparisons=len(pairs),
                   full_histories_available_for_source_addresses=False,
                   source_transaction_columns=list(TX_COLUMNS)),
        profiles=[{k: v for k, v in p.items() if not k.startswith("_")} for p in profiles],
        descriptive_evidence_groups=groups,
        pairwise_overlaps=pairs, cross_history_transaction_dependencies=dependencies,
        source_overlap=overlaps,
        limitations=[
            "Matching file hashes establishes saved-byte identity, not source authenticity or blockchain inclusion.",
            "Provider counters reconcile all supplied saved histories; cryptographic inclusion is not verified.",
            "Source transaction identifiers cover four extrema only; missing matches cannot prove complete transaction disjointness.",
            "Decoded co-addresses include inputs, change and batched outputs; shared co-addresses do not establish shared ownership.",
            "Exact address disjointness is not transaction disjointness; overlapping transactions can be multi-recipient payments.",
            "Evidence groups are conservative attribution/comparison groups, not verified mutually independent entities or incidents.",
            "The FBI source groups several heists without mapping each address to an originating incident.",
            "Donation purpose does not certify every received coin as benign; source crime labels do not transfer through transaction links.",
            "Source tables lack complete incident/entity identifiers; full entity and incident independence remains unverified.",
            "Saved histories use individual collection dates and later activity; this audit does not evaluate detection at attribution time.",
            "Pilot scores were already inspected; these cases are a descriptive development/stress-test set, not a new untouched evaluation.",
            "No precision, recall, F1, false-positive rate, calibrated probability or population performance is estimated.",
        ])


def markdown(report):
    scope = report["scope"]
    overlaps = report["source_overlap"]
    train_matches = []
    seen = set()
    for name, source in overlaps.items():
        for address, profile in source["profiles"].items():
            for tx in profile["extrema_transaction_matches"]:
                for row in tx["source_records"]:
                    key = address, tx["txid"], row["address"], name
                    if row["benchmark_split"] == "train" and key not in seen:
                        train_matches.append((address, tx, row, name))
                        seen.add(key)
    repeated_focals = {a for source in overlaps.values() for a, p in source["profiles"].items()
                       if p["focal_address_present"]}
    train_txids = {tx["txid"] for _, tx, _, _ in train_matches}
    train_addresses = {row["address"] for _, _, row, _ in train_matches}
    affected_pilots = {address for address, _, _, _ in train_matches}
    text = ["# External pilot independence audit", "",
            f"Executed at `{report['executed_at']}` on {scope['addresses']} saved pilot histories: "
            f"{scope['distinct_confirmed_transactions']:,} distinct confirmed transactions, "
            f"{scope['evidence_groups']} conservative evidence groups. "
            "All history hashes, focal identities, source records and five provider counters reconcile. "
            "Both full Real-CATS source hashes match the score reports. "
            "No model was fitted, tuned or used for prediction.", "",
            f"**{len(repeated_focals)} focal addresses occur in the source tables; "
            f"{len(affected_pilots)} pilot histories share {len(train_txids)} source-extremum transaction IDs "
            f"with {len(train_addresses)} training addresses.** "
            "Exact-address disjointness does not establish transaction independence. "
            "Transaction overlaps neither establish common ownership nor transfer source labels to the pilot. "
            "The fixed scores and threshold remain unchanged.", "",
            "## Saved descriptive scores by evidence group", "",
            "| Evidence group | Addresses | Above 0.15 | Minimum | Median | Maximum |",
            "|---|---:|---:|---:|---:|---:|"]
    for group in report["descriptive_evidence_groups"]:
        text.append(f"| {group['evidence_group']} | {group['addresses']} | "
                    f"{group['above_fixed_threshold']} | {group['score_min']:.6f} | "
                    f"{group['score_median']:.6f} | {group['score_max']:.6f} |")
    text += ["", "These are previously saved source-category scores and descriptive alert counts, "
             "not group accuracy or estimated detection performance. "
             "Group identifiers are retained from the saved attribution records; "
             "multiple addresses from one group do not become independent incidents.", "",
             "## Source coverage and provenance", "",
             "| Source table | All address rows | Rows with an extremum ID | Distinct extremum txids |",
             "|---|---:|---:|---:|"]
    for name, source in overlaps.items():
        text.append(f"| {name} | {source['source_address_rows']:,} | "
                    f"{source['source_rows_with_any_extrema']:,} | "
                    f"{source['distinct_nonempty_extrema_txids']:,} |")
    text += ["", "The source tables are pinned by byte hashes:", ""]
    text += [f"- `{name}`: `{digest}`." for name, digest in report["source_sha256"].items()]
    text += ["", "Each of the four maximum/minimum sent/received transaction-ID columns was scanned "
             "for every source row, including rows excluded from the binary benchmark. "
             "These columns are only a subset of each source address's transactions. "
             "Zero extrema matches cannot prove full-history transaction disjointness.", "",
             "The original deterministic identity split was reconstructed using address, source category "
             "and activity count only. No reserved-test predictions or predictive features were used. "
             + "; ".join(f"{name}: {count:,}" for name, count in report["split_membership_counts"].items()) + ". "
             "The JSON records source, score, history, script and split-code hashes, a logical membership hash "
             "and runtime versions. The source citations retained in history records were not newly "
             "authenticated by this offline audit.", "",
             "## Observable source overlap", "",
             "A co-address is another decoded address appearing in an input or output of any focal transaction. "
             "It can be a change address, another batched recipient, or an input participant. "
             "It is not automatically a direct counterparty, common owner or shared incident.", "",
             "| Focal address | BB co-addresses | CB co-addresses | BB extrema tx matches | CB extrema tx matches |",
             "|---|---:|---:|---:|---:|"]
    for profile in report["profiles"]:
        a = profile["address"]
        b = overlaps["BB.tsv"]["profiles"][a]
        c = overlaps["CB.tsv"]["profiles"][a]
        text.append(f"| {a} | {b['coaddress_match_count']} | {c['coaddress_match_count']} | "
                    f"{b['extrema_transaction_match_count']} | {c['extrema_transaction_match_count']} |")
    text += ["", "Each source match, source field, original split membership and observed input/output role "
             "is recorded in the JSON. Matches to source categories excluded from training are not training overlap. "
             "A transaction can match both tables; table counts must not be added to estimate unique transactions.", "",
             "### Transaction overlaps with training", "",
             "| Pilot address | Transaction ID | Training address | Tx outputs | Pilot received (sat) | Source received (sat) |",
             "|---|---|---|---:|---:|---:|"]
    for address, tx, row, name in train_matches:
        text.append(f"| {address} | {tx['txid']} | {row['address']} ({name}) | {tx['output_count']} | "
                    f"{tx['focal_observed_roles']['output_value_sat']} | "
                    f"{row['observed_roles']['output_value_sat']} |")
    if not train_matches:
        text += ["", "No source-extremum transaction matches were found in training. "
                 "This is limited to the exposed source extrema."]
    elif all(tx["focal_observed_roles"]["input_count"] == 0
             and row["observed_roles"]["input_count"] == 0
             and tx["focal_observed_roles"]["output_count"] > 0
             and row["observed_roles"]["output_count"] > 0 for _, tx, row, _ in train_matches):
        text += ["", "All listed overlaps are co-receipts: the pilot and training address both appear "
                 "as recipients, and neither supplies an input to that transaction. "
                 "This establishes shared transaction data but not a direct transfer between those addresses. "
                 "The effect of these overlaps on scores is not measured by this audit."]
    shared_pairs = [p for p in report["pairwise_overlaps"] if p["shared_coaddress_count"]]
    shared_tx_pairs = [p for p in report["pairwise_overlaps"] if p["shared_transaction_count"]]
    text += ["", "## Relations within the pilot", "",
             f"All {scope['pairwise_comparisons']} address pairs were compared. "
             f"{len(shared_tx_pairs)} pairs share at least one transaction ID; "
             f"{len(shared_pairs)} pairs share decoded co-addresses:", "",
             "| Address A | Address B | Shared co-addresses | Same evidence group |",
             "|---|---|---:|---|"]
    for p in shared_pairs:
        text.append(f"| {p['address_a']} | {p['address_b']} | {p['shared_coaddress_count']} | "
                    f"{'Yes' if p['same_evidence_group'] else 'No'} |")
    dependencies = report["cross_history_transaction_dependencies"]
    text += ["", f"{len(dependencies)} parent-output/child-input dependencies were verified across histories. "
             "Outpoint indices, values and decoded addresses agree. These links do not establish "
             "common private-key ownership; evidence groups were not merged.", ""]
    for d in dependencies:
        text.append(f"- `{d['parent_txid']}:{d['parent_output']}` is consumed by input "
                    f"{d['child_input']} of `{d['child_txid']}` ({d['value_sat']:,} sat); "
                    + "; ".join(f"parent history `{p['parent_history']}`, child history `{p['child_history']}`"
                                for p in d["history_pairs"]) + ".")
    text += ["", "## Limits", ""]
    text += [f"- {line}" for line in report["limitations"]]
    scores = " ".join(p["file"] for p in report["score_reports"])
    text += ["", "## Reproduction", "", "From `Task 2/supplementary/real_cats`, with the source checkout and saved raw artifacts available:", "",
             "```bash", "python audit_external_overlap.py /path/to/real-cats-source \\",
             f"  --scores {scores} \\",
             "  --history-root .. --history-root /path/to/raw-artifacts \\",
             "  --output external_independence_reproduced.json \\",
             "  --markdown EXTERNAL_INDEPENDENCE_REPRODUCED.md", "python -m unittest test_external_overlap -v", "```", "",
             "The command refuses to overwrite existing reports. It requires the exact saved history bytes "
             "referenced by the input score reports; no new provider calls occur. "
             "Original source tables and pilot histories remain unchanged.", ""]
    return "\n".join(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--scores", type=Path, nargs="+", required=True)
    parser.add_argument("--history-root", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        parser.error("Outputs must be new; historical reports cannot be overwritten")
    result = run(args.source, args.scores, args.history_root)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps(result["scope"], indent=2))
