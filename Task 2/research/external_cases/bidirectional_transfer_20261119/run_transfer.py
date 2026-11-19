"""Audit a pinned pair of incidents, fit a fixed tree in each direction, and replay."""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import gzip
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import statistics
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEGACY = HERE.parent / "cryptobilis_to_coldcard_20261109"
COLDCARD = HERE.parents[1] / "coldcard"
sys.path[:0] = [str(LEGACY), str(COLDCARD)]

from experiment import partition, read, recount_features, require, sha
from prepayment_pilot import normalize_prefix
from verify_results import rankings, replay

EXPECTED_COUNTS = {"coldcard": (1500, 1471, 500), "cryptobilis": (366, 329, 122)}
UNKNOWN_LABELS = (
    "independently_verified_compromise", "hardware_signing_at_event",
    "independently_verified_seed_origin",
)
REFERENCE = {"coldcard": "payment_txid_sha256", "cryptobilis": "reference_txid_sha256"}
TARGET = {
    "coldcard": "known_coldcard_core_membership",
    "cryptobilis": "cryptobilis_reference_source_membership",
}
COMPARATORS = {
    "prior_inactivity": "blocks_since_last_activity",
    "prior_balance": "balance_sat",
}
OUTPUTS = ("models.json", "predictions.json.gz", "summary.json", "metrics.csv")


def write_json(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    if path.suffix == ".gz":
        data = gzip.compress(data, mtime=0)
    with path.open("xb") as out:
        out.write(data)


def pinned(pin):
    path = (ROOT / pin["file"]).resolve()
    require(path.is_relative_to(ROOT) and sha(path) == pin["sha256"],
            f"Input fingerprint mismatch: {pin['file']}")
    return read(path)


def identifier(value):
    return hashlib.sha256(value.encode()).hexdigest()


def legacy_inputs(protocol):
    legacy = pinned(protocol["legacy_settings"])
    inputs = legacy["inputs"]
    return (
        {name: pinned(pin) for name, pin in inputs.items()
         if name in {"coldcard_view", "external_view", "overlap_evidence"}
         or name.startswith(("development_checkpoint_", "external_checkpoint_"))},
        legacy,
    )


def load_views(protocol, historical):
    incident_views = {
        "coldcard": pinned(protocol["coldcard_view"]),
        "cryptobilis": historical["external_view"],
    }
    names = incident_views["coldcard"]["predictor_allowlist"]
    require(len(set(names)) == 14, "Expected fourteen distinct predictors")
    rows = {}
    for incident, view in incident_views.items():
        require(view["schema_version"] == 2 and view["predictor_allowlist"] == names,
                f"Feature schema mismatch: {incident}")
        present = set()
        for row in view["rows"]:
            key = (incident, row["source_id"])
            require(key not in rows and row[TARGET[incident]] in (0, 1),
                    f"Duplicate ID or invalid operational label: {key}")
            require(all(row["labels"][name] is None for name in UNKNOWN_LABELS),
                    f"Unexpected verified label: {key}")
            if row["features"] is not None:
                require(set(row["features"]) == set(names), f"Invalid feature vector: {key}")
                present.add(key)
            rows[key] = row
        observed = (len(view["rows"]), len(present), sum(rows[k][TARGET[incident]] for k in present))
        require(observed == EXPECTED_COUNTS[incident], f"Unexpected pinned population: {incident}")
    return rows, names


def public_prefix(entries, row):
    entry = entries[row["source_id"]]
    require(entry["features"] == row["features"], "Checkpoint vector does not match the view")
    for field in ("address_sha256", "cutoff_height", "cutoff_block_hash", "payment_txid_sha256"):
        view_field = "reference_txid_sha256" if field == "payment_txid_sha256" and field not in row else field
        if field in entry:
            require(entry[field] == row[view_field], f"Checkpoint identity mismatch: {field}")
    return entry["prefix"]


def private_prefix(raw_root, scope, pins, row):
    manifest = pinned(pins["archive_manifest"])
    audit = pinned(pins["audit"])
    protocol = pinned(pins["protocol"])
    require(audit["verification_status"] == "passed" and audit["new_complete"] == 1
            and audit["independent_journal_replay"] == "passed", f"Missing terminal audit: {scope}")
    require(protocol["source_ids"] == [row["source_id"]], f"Protocol source mismatch: {scope}")
    file_hashes = {record["file"]: record["sha256"] for record in manifest["files"]}
    archives = list((raw_root / scope).glob("*.tar.gz"))
    require(len(archives) == 1 and sha(archives[0]) == manifest["sha256"],
            f"Missing or changed private archive: {scope}")
    folder = f"source_cohort_work_{scope}"
    wanted = {"plan.json": protocol["plan_sha256"],
              "verified_frontier.json.gz": audit["private_frontier_sha256"]}
    checked = {}
    with tarfile.open(archives[0], "r:gz") as archive:
        for name, expected in wanted.items():
            member_name = f"{folder}/{name}"
            matches = [member for member in archive if member.name == member_name]
            require(len(matches) == 1 and matches[0].isreg(), f"Invalid archive member: {scope}/{name}")
            with archive.extractfile(matches[0]) as data:
                content = data.read()
            require(hashlib.sha256(content).hexdigest() == expected == file_hashes[member_name],
                    f"Private evidence fingerprint mismatch: {scope}/{name}")
            checked[name] = json.loads(gzip.decompress(content) if name.endswith(".gz") else content)
    plan, = checked["plan.json"]
    frontier = checked["verified_frontier.json.gz"]
    require(frontier["pagination_exhausted"] is True, f"History not exhausted: {scope}")
    require(plan["pilot_id"] == row["source_id"]
            and identifier(plan["address"]) == row["address_sha256"]
            and identifier(plan["payment_txid"]) == row["payment_txid_sha256"]
            and plan["cutoff_height"] == row["cutoff_height"]
            and plan["cutoff_block_hash"] == row["cutoff_block_hash"],
            f"Private evidence identity mismatch: {scope}")
    return normalize_prefix(plan["address"], frontier["transactions"], row["cutoff_height"])


def walk_components(tokens):
    """Independent component reconstruction by walking source/token adjacency."""
    owners = defaultdict(list)
    for key, values in tokens.items():
        for value in values:
            owners[value].append(key)
    seen = set()
    groups = []
    for key in sorted(tokens):
        if key in seen:
            continue
        seen.add(key)
        pending = [key]
        group = []
        while pending:
            source = pending.pop()
            group.append(source)
            for value in tokens[source]:
                for linked in owners.pop(value, ()):
                    if linked not in seen:
                        seen.add(linked)
                        pending.append(linked)
        groups.append(sorted(group))
    return sorted(groups)


def counts(keys, rows):
    cases = sum(rows[k][TARGET[k[0]]] for k in keys)
    return {"total": len(keys), "cases": cases, "comparisons": len(keys) - cases}


def prepare(protocol, output, raw_root):
    historical, legacy = legacy_inputs(protocol)
    rows, names = load_views(protocol, historical)
    old = {r["source_id"]: r for r in historical["coldcard_view"]["rows"]}
    old_checkpoints = {
        "coldcard": {k: historical[v]["entries"] for k, v in legacy["development_checkpoints"].items()},
        "cryptobilis": {k: historical[v["checkpoint"]]["entries"]
                       for k, v in legacy["external_checkpoints"].items()},
    }
    additional = {}
    links, old_links = {}, {}
    observations = Counter()
    evidence = Counter()
    for key, row in sorted(rows.items()):
        incident, source_id = key
        is_coldcard = incident == "coldcard"
        if is_coldcard:
            prior = old[source_id]
            for field in ("address_sha256", REFERENCE[incident], "cutoff_height",
                          "cutoff_block_hash", TARGET[incident], "labels"):
                require(prior[field] == row[field], f"Original cohort changed: {source_id}/{field}")
            if prior["features"] is not None:
                require(prior["features"] == row["features"], f"Original vector changed: {source_id}")
        base_tokens = {("address", row["address_sha256"]), ("tx", row[REFERENCE[incident]])}
        tokens = set(base_tokens)
        is_added = is_coldcard and old[source_id]["features"] is None and row["features"] is not None
        if row["features"] is not None:
            provenance = row.get("precutoff_history_provenance") or row["full_history_provenance"]
            scope = provenance.get("pass_name") or provenance["chosen_pass"]
            if not is_added:
                prefix = public_prefix(old_checkpoints[incident][scope], row)
                evidence["previously_audited_vectors"] += 1
            else:
                pins = protocol["additional_coldcard_prefixes"][scope]
                if "checkpoint" in pins:
                    if scope not in additional:
                        additional[scope] = pinned(pins["checkpoint"])["entries"]
                    prefix = public_prefix(additional[scope], row)
                    evidence["additional_public_vectors"] += 1
                else:
                    prefix = private_prefix(raw_root, scope, pins, row)
                    evidence["additional_private_vectors"] += 1
            require(recount_features(prefix, row["cutoff_height"]) == row["features"],
                    f"Independent pre-cutoff feature recount failed: {key}")
            tokens.add(("vector", tuple(None if row["features"][n] is None
                                        else Fraction(row["features"][n]) for n in names)))
            tokens.update(("tx", tx["transaction_id"]) for tx in prefix)
            observations[incident] += len(prefix)
        public_key = ":".join(key)
        links[public_key] = tokens
        old_links[public_key] = base_tokens if is_added else tokens
    require(set(old) == {sid for incident, sid in rows if incident == "coldcard"},
            "Original cohort has missing IDs")
    prior_components = sorted(g["source_keys"] for g in historical["overlap_evidence"]["components"])
    require(walk_components(old_links) == prior_components, "Prior overlap audit failed to reproduce")
    components = partition(links)
    require(components == walk_components(links), "Independent overlap reconstructions disagree")
    components_by_id = {}
    for index, group in enumerate(components, start=1):
        cross = len({key.split(":", 1)[0] for key in group}) > 1
        for key in group:
            components_by_id[tuple(key.split(":", 1))] = (index, cross)
    coverage = {}
    eligibility = []
    for direction in protocol["directions"]:
        by_role = defaultdict(list)
        for key, row in sorted(rows.items()):
            incident, source_id = key
            component, cross = components_by_id[key]
            if row["features"] is None:
                role = "unavailable_train" if incident == direction["train"] else "unavailable_test"
            elif incident == direction["train"]:
                role = "train"
            else:
                role = "overlap_test" if cross else "test"
            by_role[role].append(key)
            eligibility.append({
                "direction": direction["id"], "incident": incident, "source_id": source_id,
                "role": role, "component": component, "cross_incident": cross,
            })
        require(not ({components_by_id[k][0] for k in by_role["train"]}
                     & {components_by_id[k][0] for k in by_role["test"]}), "Shared train/test group")
        coverage[direction["id"]] = {role: counts(by_role[role], rows) for role in
                                     ("train", "test", "overlap_test", "unavailable_train", "unavailable_test")}
        for role in ("train", "test"):
            support = coverage[direction["id"]][role]
            require(min(support["cases"], support["comparisons"]) >= protocol["minimum_per_class"],
                    f"Insufficient class support: {direction['id']}/{role}")
    output.mkdir(exist_ok=True)
    manifest_path = output / "eligibility.json.gz"
    write_json(manifest_path, eligibility)
    preflight = {
        "protocol_sha256": sha(HERE / "protocol.json"), "runner_sha256": sha(Path(__file__)),
        "eligibility_sha256": sha(manifest_path),
        "observations_recounted": dict(observations), "vectors_recounted": dict(evidence),
        "components": len(components), "legacy_components_reproduced": len(prior_components),
        "cross_incident_components": len({i for i, cross in components_by_id.values() if cross}),
        "independent_overlap_reconstruction": True, "directions": coverage,
        "fits_before_freeze": 0,
    }
    write_json(output / "preflight.json", preflight)
    return preflight


def frozen(protocol, output):
    selected = output / "eligibility.json.gz"
    preflight = read(output / "preflight.json")
    require(preflight["eligibility_sha256"] == sha(selected)
            and preflight["protocol_sha256"] == sha(HERE / "protocol.json")
            and preflight["runner_sha256"] == sha(Path(__file__)), "Preflight inputs changed")
    legacy = pinned(protocol["legacy_settings"])
    rows, names = load_views(protocol, {"external_view": pinned(legacy["inputs"]["external_view"])})
    eligibility = read(selected)
    return rows, names, preflight, eligibility


def select(eligibility, direction, role):
    return [(e["incident"], e["source_id"]) for e in eligibility
            if e["direction"] == direction and e["role"] == role]


def training_medians(rows, keys, names):
    medians = {}
    for name in names:
        values = [rows[k]["features"][name] for k in keys if rows[k]["features"][name] is not None]
        medians[name] = statistics.median(values) if values else 0
    return medians


def encode(row, names, medians):
    values = [row["features"][n] for n in names]
    return [medians[n] if v is None else v for n, v in zip(names, values)] + [
        int(v is None) for v in values
    ]


def label(rows, key):
    return rows[key][TARGET[key[0]]]


def baseline_value(row, field, medians):
    value = row["features"][field]
    return medians[field] if value is None else value


def fit(protocol, output):
    import numpy as np
    from sklearn.metrics import (
        average_precision_score, confusion_matrix, f1_score, precision_score,
        recall_score, roc_auc_score,
    )
    from sklearn.tree import DecisionTreeClassifier

    require(not any((output / name).exists() for name in OUTPUTS), "Use a new result directory for a refit")
    for name in ("numpy", "scikit-learn"):
        require(version(name) == protocol["software"][name], f"Unexpected software version: {name}")
    rows, names, preflight, eligibility = frozen(protocol, output)
    threshold = protocol["classification_threshold"]
    models, predictions, summary = {}, [], {}
    for direction in protocol["directions"]:
        run = direction["id"]
        train, test = (select(eligibility, run, role) for role in ("train", "test"))
        medians = training_medians(rows, train, names)
        training_labels = [label(rows, k) for k in train]
        testing_labels = [label(rows, k) for k in test]
        tree = DecisionTreeClassifier(**protocol["model"])
        tree.fit(np.array([encode(rows[k], names, medians) for k in train], dtype=np.float32),
                 training_labels)
        require(list(tree.classes_) == [0, 1], "Unexpected model class ordering")
        x = np.array([encode(rows[k], names, medians) for k in test], dtype=np.float32)
        scores = tree.predict_proba(x)[:, 1]
        leaves = tree.apply(x)
        decisions = scores >= threshold
        model = tree.tree_
        models[run] = {
            "feature_names": names + [n + "__missing" for n in names], "medians": medians,
            "params": protocol["model"], "classification_threshold": threshold,
            "nodes": [
                {"left": int(model.children_left[i]), "right": int(model.children_right[i]),
                 "feature_index": int(model.feature[i]), "threshold": float(model.threshold[i]),
                 "positive_probability": float(model.value[i, 0, 1]),
                 "sample_count": int(model.n_node_samples[i])}
                for i in range(model.node_count)
            ],
        }
        ranks = {"tree": scores, "training_prevalence": [statistics.mean(training_labels)] * len(test)}
        ranks.update({key: [baseline_value(rows[k], field, medians) for k in test]
                      for key, field in COMPARATORS.items()})
        tn, fp, fn, tp = (int(v) for v in confusion_matrix(testing_labels, decisions, labels=[0, 1]).ravel())
        metrics = {
            "precision": float(precision_score(testing_labels, decisions, zero_division=0)),
            "recall": float(recall_score(testing_labels, decisions, zero_division=0)),
            "f1": float(f1_score(testing_labels, decisions, zero_division=0)),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "rankings": {key: {"average_precision": float(average_precision_score(testing_labels, vals)),
                               "roc_auc": float(roc_auc_score(testing_labels, vals))}
                         for key, vals in ranks.items()},
        }
        for i, key in enumerate(test):
            predictions.append({
                "direction": run, "incident": key[0], "source_id": key[1],
                "membership": testing_labels[i], "decision": int(decisions[i]), "leaf": int(leaves[i]),
                "scores": {name: float(values[i]) for name, values in ranks.items()},
            })
        summary[run] = {"population": preflight["directions"][run], "metrics": metrics}
    write_json(output / "models.json", models)
    write_json(output / "predictions.json.gz", predictions)
    write_json(output / "summary.json", {"fits": len(models), "directions": summary})
    with (output / "metrics.csv").open("x", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["direction", "train_n", "test_n", "test_link_exclusions",
                         "test_unavailable", "precision", "recall", "f1",
                         "average_precision", "roc_auc", "inactivity_average_precision",
                         "tp", "fp", "fn", "tn"])
        for name, result in summary.items():
            pop = result["population"]
            m = result["metrics"]
            writer.writerow([name, *(pop[k]["total"] for k in
                                     ("train", "test", "overlap_test", "unavailable_test")),
                             m["precision"], m["recall"], m["f1"],
                             m["rankings"]["tree"]["average_precision"], m["rankings"]["tree"]["roc_auc"],
                             m["rankings"]["prior_inactivity"]["average_precision"],
                             m["tp"], m["fp"], m["fn"], m["tn"]])
    return summary


def verify(protocol, output):
    rows, names, preflight, eligibility = frozen(protocol, output)
    models = read(output / "models.json")
    predictions = read(output / "predictions.json.gz")
    summary = read(output / "summary.json")
    require(summary["fits"] == len(protocol["directions"]), "Unexpected fit count")
    prediction_count = 0
    for direction in protocol["directions"]:
        run = direction["id"]
        train, test = (select(eligibility, run, role) for role in ("train", "test"))
        require(all(k[0] == direction["train"] for k in train)
                and all(k[0] == direction["test"] for k in test), "Incidents mixed across roles")
        model = models[run]
        medians = training_medians(rows, train, names)
        require(medians == model["medians"] and model["params"] == protocol["model"], "Model inputs differ")
        prevalence = statistics.mean(label(rows, k) for k in train)
        supports = Counter()
        positive_weight = defaultdict(float)
        total_weight = defaultdict(float)
        class_counts = Counter(label(rows, k) for k in train)
        for key in train:
            truth = label(rows, key)
            weight = len(train) / (2 * class_counts[truth])
            _, _, visited = replay(model, rows[key])
            for node in visited:
                supports[node] += 1
                positive_weight[node] += truth * weight
                total_weight[node] += weight
        for i, node in enumerate(model["nodes"]):
            require(node["sample_count"] == supports[i]
                    and math.isclose(node["positive_probability"], positive_weight[i] / total_weight[i],
                                     rel_tol=0, abs_tol=1e-12), "Training node supports differ")
        expected = summary["directions"][run]
        require(expected["population"] == preflight["directions"][run], "Population summary differs")
        chosen = [p for p in predictions if p["direction"] == run]
        require([(p["incident"], p["source_id"]) for p in chosen] == test, "Evaluation rows differ")
        labels = [label(rows, k) for k in test]
        threshold = protocol["classification_threshold"]
        c = Counter()
        for key, truth, p in zip(test, labels, chosen):
            score, leaf, _ = replay(model, rows[key])
            require(p["leaf"] == leaf and p["scores"]["tree"] == score
                    and p["membership"] == truth and p["decision"] == int(score >= threshold),
                    f"Float32 tree replay disagrees: {run}/{key}")
            require(p["scores"]["training_prevalence"] == prevalence, "Prevalence baseline differs")
            require(all(p["scores"][n] == baseline_value(rows[key], f, medians)
                        for n, f in COMPARATORS.items()), "Baseline prediction differs")
            c[truth, p["decision"]] += 1
        m = expected["metrics"]
        tn, fp, fn, tp = (c[a, b] for a, b in ((0, 0), (0, 1), (1, 0), (1, 1)))
        require((tp, fp, fn, tn) == (m["tp"], m["fp"], m["fn"], m["tn"]), "Confusion counts differ")
        ratios = {"precision": tp / (tp + fp) if tp + fp else 0, "recall": tp / (tp + fn),
                  "f1": 2 * tp / (2 * tp + fp + fn)}
        require(all(math.isclose(m[k], v, abs_tol=1e-12, rel_tol=0) for k, v in ratios.items()),
                "Classification metrics differ")
        for metric, values in m["rankings"].items():
            recomputed = rankings(labels, [p["scores"][metric] for p in chosen])
            require(all(math.isclose(values[k], v, abs_tol=1e-12, rel_tol=0)
                        for k, v in recomputed.items()), "Ranking metrics differ")
        prediction_count += len(chosen)
    require(prediction_count == len(predictions), "Unexpected additional predictions")
    return {"verified_predictions": prediction_count, "verified_directions": len(models),
            "model_refits_in_verification": 0, "metric_sets_recomputed": 4 * len(models)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=("prepare", "fit", "verify"))
    parser.add_argument("--output", type=Path, default=HERE)
    parser.add_argument("--raw-archives", type=Path)
    args = parser.parse_args()
    protocol = read(HERE / "protocol.json")
    if args.step == "prepare":
        if args.raw_archives is None:
            parser.error("prepare requires --raw-archives")
        result = prepare(protocol, args.output, args.raw_archives)
    elif args.step == "fit":
        result = fit(protocol, args.output)
    else:
        result = verify(protocol, args.output)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
