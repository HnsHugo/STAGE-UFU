# Part 4 — Evaluate generalization and understand errors

[Previous: Part 3](../part_3_classifier/README.md) · [Main path](../README.md) · [Next: Part 5](../part_5_cross_case/README.md)

## Goal

Separate success on a small exercise from performance on different transaction groups. This part evaluates the extended candidate-relation target, not exactly the payment-to-address target of Part 3.

## Read in this order

1. [Random and chronological experiments](../research/coldcard/EXPERIMENT.md): why a favorable random split is not enough.
2. [Leave-one-candidate-group-out results](../research/coldcard/GROUPED_EXPERIMENT.md): keep an entire candidate group outside each training fold.
3. [Simple univariate baselines](../research/coldcard/GROUPED_BASELINES_20261016.md): compare the full tree with single-feature rules learned on training only.

## Key results

| Method | Candidate relations recovered | Alerts on unattributed background |
| --- | ---: | ---: |
| Extended grouped tree | 874 / 1,070 | 1,072 |
| Fee-rate-only stump | 1,036 / 1,070 | 7,878 |
| Output-count-only stump | 1,070 / 1,070 | 54,510 |

The full tree has pooled proxy F1 57.96% and recall 81.68%, but mean recall giving each group equal weight is 55.20%. One group of 34 is entirely missed. The full tree reduces background alerts but also misses candidates recovered by a simpler baseline.

Background alerts are not certified false positives. The four groups belong to one source-attributed case; unknown background relationships and missing blocks prevent a claim of independent actors or incidents. This remains internal validation.

## Code and reproduction

Use [train_grouped.py](../research/coldcard/train_grouped.py) for the original grouped experiment and [compare_grouped_baselines.py](../research/coldcard/compare_grouped_baselines.py) for the fixed diagnostic baselines. Historical metrics are [saved here](../research/coldcard/grouped_results_20261008/metrics.json).

```bash
python "Task 2/research/coldcard/train_grouped.py" /path/to/transactions.csv.gz \
  /path/to/candidate_groups.json /path/to/manifest.json /path/to/new_grouped_output
```

Do not rerun historical experiments simply to improve the displayed score. See Part 5 for adding a genuinely different case.

## What to explain

“The model learns a signal, but performance varies by group. The failure cases and baseline trade-offs show why dataset diversity and label quality matter.”
