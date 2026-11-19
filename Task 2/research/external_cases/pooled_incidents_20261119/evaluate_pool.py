"""Evaluate pooled Coldcard and CryptoBilis with shared groups held out."""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
WITHIN = HERE.parent / "within_incident_20261119"
sys.path.insert(0, str(WITHIN))

import evaluate_within as within

prior = within.prior


def input_data(protocol):
    for name, expected in protocol["within_incident_pins"].items():
        prior.require(prior.sha(WITHIN / name) == expected, f"Pinned input differs: {name}")
    baseline = prior.read(WITHIN / "protocol.json")
    prior.require(baseline["population"] == protocol["population"], "Incident coverage changed")
    return within.input_data(baseline)


def fold_keys(records, fold):
    train = [within.member(record) for record in records if record["fold"] != fold]
    test = [within.member(record) for record in records if record["fold"] == fold]
    return train, test


def audit_folds(protocol, rows, groups, records):
    complete = {key for key, row in rows.items() if row["features"] is not None}
    prior.require(len(records) == len(complete) and {within.member(r) for r in records} == complete,
                  "Each complete address must be evaluated once")
    k = protocol["split"]["n_splits"]
    assignments = {}
    for record in records:
        key = within.member(record)
        group, fold = record["component"], record["fold"]
        prior.require(group == groups[key] and 1 <= fold <= k, f"Invalid assignment: {key}")
        prior.require(assignments.setdefault(group, fold) == fold,
                      f"Shared component {group} crosses evaluation folds")

    observed = {}
    for incident, expected in protocol["population"].items():
        selected = [key for key in rows if key[0] == incident]
        ready = [key for key in selected if key in complete]
        counts = {"available": len(ready), "unavailable": len(selected) - len(ready)}
        prior.require(counts == expected, f"Coverage changed: {incident}")
        observed[incident] = {**counts, "cases": sum(prior.label(rows, key) for key in ready)}

    folds = []
    for fold in range(1, k + 1):
        train, test = fold_keys(records, fold)
        train_groups, test_groups = ({groups[key] for key in partition} for partition in (train, test))
        prior.require(not train_groups & test_groups, f"Group leakage in fold {fold}")
        support = {"fold": fold, "train": len(train), "test": len(test), "test_groups": len(test_groups)}
        for role, keys in (("train", train), ("test", test)):
            by_incident = {}
            for incident in observed:
                subset = [key for key in keys if key[0] == incident]
                counts = prior.counts(subset, rows)
                prior.require(min(counts["cases"], counts["comparisons"])
                              >= protocol["split"]["minimum_per_incident_class"],
                              f"Insufficient class support: fold {fold}/{role}/{incident}")
                by_incident[incident] = counts
            support[f"{role}_by_incident"] = by_incident
        folds.append(support)
    return {"incidents": observed, "folds": folds, "complete": len(complete),
            "components": len(assignments), "largest_component": max(Counter(r["component"] for r in records).values())}


def prepare(protocol, output):
    from sklearn.model_selection import StratifiedGroupKFold

    within.check_software(protocol)
    rows, _, groups, _ = input_data(protocol)
    keys = sorted(key for key, row in rows.items() if row["features"] is not None)
    strata = [f"{key[0]}:{prior.label(rows, key)}" for key in keys]
    split = protocol["split"]
    prior.require(split["method"] == "StratifiedGroupKFold", "Unexpected split method")
    cv = StratifiedGroupKFold(n_splits=split["n_splits"], shuffle=split["shuffle"],
                              random_state=split["random_state"])
    records = []
    held_out_indices = cv.split(keys, strata, [groups[key] for key in keys])
    for fold, (_, test) in enumerate(held_out_indices, start=1):
        for i in test:
            incident, source_id = keys[i]
            records.append({"incident": incident, "source_id": source_id,
                            "fold": fold, "component": groups[keys[i]]})
    records.sort(key=within.member)
    audit = audit_folds(protocol, rows, groups, records)
    output.mkdir(parents=True, exist_ok=True)
    path = output / "folds.json.gz"
    prior.write_json(path, records)
    preflight = {"fits_before_freeze": 0, "protocol_sha256": prior.sha(HERE / "protocol.json"),
                 "runner_sha256": prior.sha(Path(__file__)), "folds_sha256": prior.sha(path),
                 "population_audit": audit}
    prior.write_json(output / "preflight.json", preflight)
    return audit


def frozen(protocol, output):
    preflight = prior.read(output / "preflight.json")
    path = output / "folds.json.gz"
    prior.require(preflight["protocol_sha256"] == prior.sha(HERE / "protocol.json")
                  and preflight["runner_sha256"] == prior.sha(Path(__file__))
                  and preflight["folds_sha256"] == prior.sha(path), "Pre-fit files changed")
    rows, names, groups, params = input_data(protocol)
    records = prior.read(path)
    prior.require(audit_folds(protocol, rows, groups, records) == preflight["population_audit"],
                  "Fold coverage or linked groups changed")
    return rows, names, params, records


def summarize(protocol, predictions, ranking):
    results = {}
    for cohort in ("global", *protocol["population"]):
        selected = [r for r in predictions if cohort == "global" or r["incident"] == cohort]
        results[cohort] = {
            "pooled": within.metrics_from_predictions(selected, ranking),
            "folds": {
                str(fold): within.metrics_from_predictions([r for r in selected if r["fold"] == fold], ranking)
                for fold in range(1, protocol["split"]["n_splits"] + 1)
            },
        }
    return results


def fit(protocol, output):
    import numpy as np
    from sklearn.metrics import average_precision_score, roc_auc_score
    from sklearn.tree import DecisionTreeClassifier

    prior.require(not any((output / name).exists() for name in within.FIT_OUTPUTS),
                  "Existing fitted outputs are immutable")
    within.check_software(protocol)
    rows, names, params, records = frozen(protocol, output)
    threshold = protocol["classification_threshold"]
    models, predictions = {}, []
    for fold in range(1, protocol["split"]["n_splits"] + 1):
        train, test = fold_keys(records, fold)
        medians = prior.training_medians(rows, train, names)

        def matrix(keys):
            return np.array([prior.encode(rows[key], names, medians) for key in keys], dtype=np.float32)

        tree = DecisionTreeClassifier(**params).fit(matrix(train), [prior.label(rows, key) for key in train])
        prior.require(list(tree.classes_) == [0, 1], "Invalid estimator class ordering")
        held_out = matrix(test)
        models[str(fold)] = within.pinned_tree_export(tree, names, medians)
        for key, raw_score, leaf in zip(test, tree.predict_proba(held_out)[:, 1], tree.apply(held_out)):
            score = float(raw_score)
            baselines = {name: prior.baseline_value(rows[key], field, medians)
                         for name, field in within.BASELINES.items()}
            predictions.append({"incident": key[0], "source_id": key[1], "fold": fold,
                                "membership": prior.label(rows, key), "leaf": int(leaf),
                                "scores": {"tree": score, **baselines}, "decision": int(score >= threshold)})

    def sklearn_rank(labels, scores):
        return {"average_precision": float(average_precision_score(labels, scores)),
                "roc_auc": float(roc_auc_score(labels, scores))}

    results = summarize(protocol, predictions, sklearn_rank)
    prior.write_json(output / "models.json.gz", models)
    prior.write_json(output / "predictions.json.gz", predictions)
    prior.write_json(output / "summary.json", {"model_fits": len(models), "cohorts": results})
    within.write_csv(output / "metrics.csv", results)
    return results


def verify(protocol, output):
    rows, names, _, records = frozen(protocol, output)
    stored = prior.read(output / "summary.json")
    models = prior.read(output / "models.json.gz")
    predictions = prior.read(output / "predictions.json.gz")
    by_key = {within.member(r): r for r in predictions}
    prior.require(len(by_key) == len(predictions) == len(records)
                  and set(by_key) == {within.member(r) for r in records}, "Missing or repeated predictions")
    k = protocol["split"]["n_splits"]
    prior.require(stored["model_fits"] == k and set(models) == {str(i) for i in range(1, k + 1)},
                  "Unexpected fold-model count")
    threshold = protocol["classification_threshold"]
    for fold in range(1, k + 1):
        train, test = fold_keys(records, fold)
        model = models[str(fold)]
        medians = prior.training_medians(rows, train, names)
        prior.require(medians == model["medians"], "Exported imputation differs from training-fold medians")
        class_counts = Counter(prior.label(rows, key) for key in train)
        supports, total_weights, positive_weights = Counter(), defaultdict(float), defaultdict(float)
        for key in train:
            label = prior.label(rows, key)
            weight = len(train) / (2 * class_counts[label])
            _, _, path = prior.replay(model, rows[key])
            for node in path:
                supports[node] += 1
                total_weights[node] += weight
                positive_weights[node] += label * weight
        for node, fields in enumerate(model["nodes"]):
            prior.require(fields["sample_count"] == supports[node] and math.isclose(
                fields["positive_probability"], positive_weights[node] / total_weights[node],
                rel_tol=0, abs_tol=1e-12), "Exported node differs from training-fold support")
        for key in test:
            record = by_key[key]
            score, leaf, _ = prior.replay(model, rows[key])
            expected = (fold, prior.label(rows, key), leaf, score, int(score >= threshold))
            actual = (record["fold"], record["membership"], record["leaf"],
                      record["scores"]["tree"], record["decision"])
            prior.require(actual == expected, f"Prediction differs for held-out row {key}")
            for name, field in within.BASELINES.items():
                prior.require(record["scores"][name] == prior.baseline_value(rows[key], field, medians),
                              "Baseline score differs")
    within.compare(stored["cohorts"], summarize(protocol, predictions, prior.rankings))
    return {"oof_predictions_replayed": len(predictions), "fold_models_verified": k,
            "train_test_component_overlap": 0, "verification_fits": 0}


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
