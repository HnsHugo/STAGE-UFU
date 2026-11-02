# Part 4 — Evaluate generalization and understand errors

[Previous: Part 3](../part_3_classifier/README.md) · [Main path](../README.md) · [Next: Part 5](../part_5_cross_case/README.md)

## Goal

Explain what each fixed evaluation establishes, keeping the new source-membership
target separate from the historical transaction candidate-relation target.

## Source-address membership evaluation — 2 November 2026

The [research write-up](../source_address_study/README.md) reports the unchanged
grouped split and held-out development results. All 918 observed-link components
remain in one partition each; no measured shared prior reference, reference TXID
or identical full vector crosses partitions. This does not establish unknown
entity links or independent incidents.

| Partition | Addresses | Membership TP / FP / FN / TN | Membership F1 |
| --- | ---: | --- | ---: |
| Validation | 111 | 56 / 1 / 0 / 54 | 0.991150 |
| Test | 234 | 97 / 1 / 1 / 135 | 0.989796 |

The fixed test AP is 0.993757 and ROC-AUC 0.994748. Inactivity alone already has
AP 0.982880. The missing case `cohort_0191` was recently active; the outside-core
comparison `comparison_0401` resembles the older funded case profile. These are
membership errors, not adjudicated theft/device errors. Exactly 122 selected
comparisons remain unscored, with disproportionately large saved current
histories. The study covers one previously inspected incident; no independent-
incident, untouched-test or prospective claim is made. No tuning uses these
validation/test outcomes. The [saved interpretation](../research/coldcard/source_membership_baseline_20261102_162335/INTERPRETATION.md)
and report explain the rule, coverage bias and unknown labels.

## Historical transaction candidate-relation evaluation

The sections below evaluate the extended transaction candidate-relation target,
which also differs from the classroom payment-to-address target of Part 3.

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
