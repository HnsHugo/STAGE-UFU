"""Evaluate the two pinned incident cohorts with grouped out-of-fold predictions."""
import argparse
from collections import Counter, defaultdict
import csv
from importlib.metadata import version
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
TRANSFER = HERE.parent / "bidirectional_transfer_20261119"
sys.path.insert(0, str(TRANSFER))

import run_transfer as prior

BASELINES = prior.COMPARATORS
FIT_OUTPUTS = ("models.json.gz", "predictions.json.gz", "summary.json", "metrics.csv")


def input_data(protocol):
    for name, expected in protocol["input_pins"].items():
        prior.require(prior.sha(TRANSFER / name) == expected, f"Pinned input differs: {name}")
    old = prior.read(TRANSFER / "protocol.json")
    rows, names, _, eligibility = prior.frozen(old, TRANSFER)
    components = defaultdict(set)
    for record in eligibility:
        components[record["incident"], record["source_id"]].add(record["component"])
    prior.require(set(components) == set(rows) and all(len(v) == 1 for v in components.values()),
                  "Ambiguous components or missing selected addresses")
    observed = {key: next(iter(values)) for key, values in components.items()}
    return rows, names, observed, old["model"]


def check_software(protocol):
    for name, expected in protocol["software"].items():
        prior.require(version(name) == expected, f"Expected {name} {expected}")


def member(record):
    return record["incident"], record["source_id"]


def split_keys(records, incident, fold):
    active = [record for record in records if record["incident"] == incident]
    return ([member(record) for record in active if record["fold"] != fold],
            [member(record) for record in active if record["fold"] == fold])


def check_folds(protocol, rows, groups, records):
    applicable = {key for key, row in rows.items() if row["features"] is not None}
    prior.require(len(records) == len(applicable) and {member(r) for r in records} == applicable,
                  "Every complete row must appear in exactly one evaluation fold")
    assignments = {}
    for r in records:
        key = member(r)
        prior.require(r["component"] == groups[key], f"Component changed: {key}")
        by_group = key[0], r["component"]
        prior.require(assignments.setdefault(by_group, r["fold"]) == r["fold"],
                      f"Connected component split across folds: {by_group}")
    k = protocol["split"]["n_splits"]
    minimum = protocol["split"]["minimum_class_support"]
    support = {}
    for incident, expected in protocol["population"].items():
        keys = {key for key in rows if key[0] == incident}
        complete = keys & applicable
        prior.require((len(complete), len(keys - complete)) == (expected["available"], expected["unavailable"]),
                      f"Unexpected cohort coverage: {incident}")
        tested = set()
        summaries = []
        for fold in range(1, k + 1):
            train, test = split_keys(records, incident, fold)
            train_groups = {groups[key] for key in train}
            test_groups = {groups[key] for key in test}
            prior.require(not train_groups & test_groups and not tested.intersection(test)
                          and set(train).union(test) == complete, "Held-out group assignment changed")
            observed = {"fold": fold, "train": prior.counts(train, rows), "test": prior.counts(test, rows),
                        "test_groups": len(test_groups)}
            for role in ("train", "test"):
                prior.require(min(observed[role]["cases"], observed[role]["comparisons"]) >= minimum,
                              f"Insufficient {role} support: {incident}/{fold}")
            tested.update(test)
            summaries.append(observed)
        prior.require(tested == complete, f"Not all complete addresses were scored: {incident}")
        support[incident] = {"population": prior.counts(list(complete), rows),
                             "incomplete": len(keys - complete), "groups": len({groups[k] for k in complete}),
                             "largest_group": max(Counter(groups[k] for k in complete).values()),
                             "folds": summaries}
    return support


def prepare(protocol, output):
    from sklearn.model_selection import StratifiedGroupKFold

    check_software(protocol)
    rows, _, groups, _ = input_data(protocol)
    settings = protocol["split"]
    prior.require(settings["method"] == "StratifiedGroupKFold", "Unexpected splitter")
    records = []
    for incident in protocol["population"]:
        keys = sorted(key for key in rows if key[0] == incident and rows[key]["features"] is not None)
        splitter = StratifiedGroupKFold(n_splits=settings["n_splits"], shuffle=settings["shuffle"],
                                        random_state=settings["random_state"])
        for fold, (_, test_indices) in enumerate(
                splitter.split(keys, [prior.label(rows, k) for k in keys], [groups[k] for k in keys]), start=1):
            records.extend({"incident": incident, "source_id": keys[i][1],
                            "component": groups[keys[i]], "fold": fold}
                           for i in test_indices)
    records.sort(key=member)
    support = check_folds(protocol, rows, groups, records)
    output.mkdir(parents=True, exist_ok=True)
    path = output / "folds.json.gz"
    prior.write_json(path, records)
    preflight = {"fits_before_freeze": 0, "protocol_sha256": prior.sha(HERE / "protocol.json"),
                 "runner_sha256": prior.sha(Path(__file__)), "folds_sha256": prior.sha(path),
                 "incidents": support}
    prior.write_json(output / "preflight.json", preflight)
    return preflight


def frozen(protocol, output):
    preflight = prior.read(output / "preflight.json")
    folds = output / "folds.json.gz"
    prior.require(preflight["protocol_sha256"] == prior.sha(HERE / "protocol.json")
                  and preflight["runner_sha256"] == prior.sha(Path(__file__))
                  and preflight["folds_sha256"] == prior.sha(folds), "Pre-fit files changed")
    rows, names, groups, params = input_data(protocol)
    records = prior.read(folds)
    prior.require(check_folds(protocol, rows, groups, records) == preflight["incidents"],
                  "Class or component support changed")
    return rows, names, params, records, preflight


def pinned_tree_export(tree, names, medians):
    fitted = tree.tree_
    return {
        "feature_names": names + [f"{name}__missing" for name in names], "medians": medians,
        "nodes": [
            {"left": int(fitted.children_left[i]), "right": int(fitted.children_right[i]),
             "feature_index": int(fitted.feature[i]), "threshold": float(fitted.threshold[i]),
             "positive_probability": float(fitted.value[i, 0, 1]),
             "sample_count": int(fitted.n_node_samples[i])}
            for i in range(fitted.node_count)
        ],
    }


def metrics_from_predictions(selected, ranking):
    labels = [r["membership"] for r in selected]
    outcomes = Counter((r["membership"], r["decision"]) for r in selected)
    tn, fp, fn, tp = (outcomes[k] for k in ((0, 0), (0, 1), (1, 0), (1, 1)))
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn)
    return {"n": len(labels), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": precision, "recall": recall, "f1": 2 * tp / (2 * tp + fp + fn),
            "rankings": {name: ranking(labels, [r["scores"][name] for r in selected])
                         for name in ("tree", *BASELINES)}}


def summary(protocol, predictions, ranking):
    results = {}
    for incident in protocol["population"]:
        selected = [r for r in predictions if r["incident"] == incident]
        results[incident] = {
            "pooled": metrics_from_predictions(selected, ranking),
            "folds": {str(fold): metrics_from_predictions([r for r in selected if r["fold"] == fold], ranking)
                      for fold in range(1, protocol["split"]["n_splits"] + 1)},
        }
    return results


def write_csv(path, results):
    with path.open("x", newline="") as out:
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(["incident", "fold", "test_n", "precision", "recall", "f1",
                         "average_precision", "roc_auc", "inactivity_average_precision",
                         "balance_average_precision", "tp", "fp", "fn", "tn"])
        for incident, metrics in results.items():
            for fold, m in [("pooled", metrics["pooled"]), *metrics["folds"].items()]:
                writer.writerow([incident, fold, m["n"], m["precision"], m["recall"], m["f1"],
                                 m["rankings"]["tree"]["average_precision"], m["rankings"]["tree"]["roc_auc"],
                                 m["rankings"]["prior_inactivity"]["average_precision"],
                                 m["rankings"]["prior_balance"]["average_precision"],
                                 m["tp"], m["fp"], m["fn"], m["tn"]])


def fit(protocol, output):
    import numpy as np
    from sklearn.metrics import average_precision_score, roc_auc_score
    from sklearn.tree import DecisionTreeClassifier

    prior.require(not any((output / name).exists() for name in FIT_OUTPUTS),
                  "Existing fitted results are immutable")
    check_software(protocol)
    rows, names, params, records, _ = frozen(protocol, output)
    threshold = protocol["classification_threshold"]
    models = defaultdict(dict)
    predictions = []
    for incident in protocol["population"]:
        for fold in range(1, protocol["split"]["n_splits"] + 1):
            train, test = split_keys(records, incident, fold)
            medians = prior.training_medians(rows, train, names)
            x_train = np.array([prior.encode(rows[key], names, medians) for key in train], dtype=np.float32)
            x_test = np.array([prior.encode(rows[key], names, medians) for key in test], dtype=np.float32)
            tree = DecisionTreeClassifier(**params).fit(x_train, [prior.label(rows, key) for key in train])
            prior.require(list(tree.classes_) == [0, 1], "Invalid tree class order")
            scores = tree.predict_proba(x_test)[:, 1]
            leaves = tree.apply(x_test)
            models[incident][str(fold)] = pinned_tree_export(tree, names, medians)
            for i, key in enumerate(test):
                score = float(scores[i])
                baselines = {name: prior.baseline_value(rows[key], field, medians)
                             for name, field in BASELINES.items()}
                predictions.append({"incident": incident, "source_id": key[1], "fold": fold,
                                    "membership": prior.label(rows, key), "leaf": int(leaves[i]),
                                    "scores": {"tree": score, **baselines}, "decision": int(score >= threshold)})

    def sklearn_rank(labels, scores):
        return {"average_precision": float(average_precision_score(labels, scores)),
                "roc_auc": float(roc_auc_score(labels, scores))}

    results = summary(protocol, predictions, sklearn_rank)
    prior.write_json(output / "models.json.gz", models)
    prior.write_json(output / "predictions.json.gz", predictions)
    prior.write_json(output / "summary.json", {"model_fits": sum(len(v) for v in models.values()),
                                               "incidents": results})
    write_csv(output / "metrics.csv", results)
    return results


def compare(expected, observed):
    if isinstance(expected, dict):
        prior.require(set(observed) == set(expected), "Metric keys differ")
        for key in expected:
            compare(expected[key], observed[key])
    else:
        prior.require(math.isclose(expected, observed, rel_tol=0, abs_tol=1e-12),
                      f"Metric changed: {expected} != {observed}")


def verify(protocol, output):
    rows, names, _, records, _ = frozen(protocol, output)
    models = prior.read(output / "models.json.gz")
    predictions = prior.read(output / "predictions.json.gz")
    stored = prior.read(output / "summary.json")
    by_key = {member(r): r for r in predictions}
    prior.require(len(predictions) == len(by_key) == len(records)
                  and set(by_key) == {member(r) for r in records}, "Evaluation predictions are not one per row")
    threshold = protocol["classification_threshold"]
    fit_count = 0
    for incident in protocol["population"]:
        for fold in range(1, protocol["split"]["n_splits"] + 1):
            train, test = split_keys(records, incident, fold)
            exported = models[incident][str(fold)]
            fit_count += 1
            medians = prior.training_medians(rows, train, names)
            prior.require(exported["medians"] == medians, "Imputation saw an evaluation row")
            # Replay the training population through the serialized tree to verify node support.
            supports, weights, positive_weights = Counter(), defaultdict(float), defaultdict(float)
            class_counts = Counter(prior.label(rows, key) for key in train)
            for key in train:
                label = prior.label(rows, key)
                weight = len(train) / (2 * class_counts[label])
                _, _, path = prior.replay(exported, rows[key])
                for node in path:
                    supports[node] += 1
                    weights[node] += weight
                    positive_weights[node] += label * weight
            for node, values in enumerate(exported["nodes"]):
                prior.require(values["sample_count"] == supports[node] and math.isclose(
                    values["positive_probability"], positive_weights[node] / weights[node],
                    rel_tol=0, abs_tol=1e-12), "Weighted training node support differs")
            for key in test:
                p = by_key[key]
                score, leaf, _ = prior.replay(exported, rows[key])
                prior.require((p["fold"], p["leaf"], p["membership"], p["decision"], p["scores"]["tree"]) ==
                              (fold, leaf, prior.label(rows, key), int(score >= threshold), score),
                              f"Held-out prediction differs: {key}")
                for name, field in BASELINES.items():
                    prior.require(p["scores"][name] == prior.baseline_value(rows[key], field, medians),
                                  "Baseline score differs")
    prior.require(stored["model_fits"] == fit_count, "Incorrect fit count")
    compare(stored["incidents"], summary(protocol, predictions, prior.rankings))
    return {"out_of_fold_predictions_verified": len(predictions), "training_partitions_verified": fit_count,
            "group_overlap": 0, "verification_fits": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=("prepare", "fit", "verify"))
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    action = {"prepare": prepare, "fit": fit, "verify": verify}[args.step]
    result = action(prior.read(HERE / "protocol.json"), args.output)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
