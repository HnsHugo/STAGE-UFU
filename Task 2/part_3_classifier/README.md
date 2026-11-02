# Part 3 — Interpretable transaction and source-address classifiers

[Previous: Part 2](../part_2_dataset/README.md) · [Main path](../README.md) · [Next: Part 4](../part_4_validation/README.md)

## Goal

Explain the completed source-address membership baseline and preserve the earlier
classroom transaction exercise as a separate target, unit and evaluation.

## Source-address membership baseline — 2 November 2026

The [research write-up](../source_address_study/README.md) explains the current
address-level model. One depth-3 tree with a minimum of 20 training addresses per
leaf, balanced class weights and seed 42 was fitted on 1,033 training addresses.
The original 918-component hash partition assigns 111 addresses to validation
and 234 to test. Training-only medians and fourteen fixed missingness indicators
accompany the fourteen unchanged prior-block predictors. The fixed membership
decision includes scores equal to 0.5. No parameter search or all-row refit followed.

The tree uses prior balance and inactivity. Test membership F1 is 0.989796, with
one false-positive and one false-negative membership. This is retrospective
development within one previously inspected incident, with 122 comparisons
excluded for unavailable prefixes. It does not identify verified theft or devices.

- [Frozen model, rules and all scores](../research/coldcard/source_membership_baseline_20261102_162335/README.md).
- [Rule and membership-error interpretation](../research/coldcard/source_membership_baseline_20261102_162335/INTERPRETATION.md).
- [Methods and results ready for the article](../source_address_study/README.md#article-integration).

The write-up and artifact verification replay saved results without training.
See Part 4 for the membership confusion counts, simple rankings and limits.

## Historical classroom transaction exercise

The earlier exercise uses 100 transactions paying the course address, 100
comparisons and a different interpretable decision tree. Its results below remain
unchanged and must not be combined with the source-address membership score.

## Open these first

1. [Exercise method and results](../research/coldcard/COURSE_EXERCISE.md).
2. [The readable decision tree](../research/coldcard/course_results_20261014/tree.txt).
3. [Detailed metrics and sampling](../research/coldcard/course_results_20261014/report.json).
4. [The 200-row cohort and its train/test membership](../research/coldcard/course_results_20261014/cohort.csv).

The sample is deterministic and comparisons are matched by block. Training has 140 rows; the sample test has 60 rows. The fixed tree has maximum depth 4, minimum 5 rows per leaf and seed 42. The ten course features are described in Part 2.

## Result and meaning

The tree classifies all 60 sample test rows correctly. It mainly relies on fees. Both sides still share the same address/case and blocks, so this is a successful classroom exercise, not evidence of a general theft or hardware-wallet detector.

When applied to 492,135 unused unattributed transactions, it flags 8,158. Their output addresses are review leads, not confirmed new thefts. [Candidate review](../research/coldcard/candidate_review_20261015.json) records the limited follow-up.

## Reproduce

With the separately supplied inputs and a new output directory:

```bash
python "Task 2/research/coldcard/course_baseline.py" "/path/to/blocos(1).tgz" \
  /path/to/parents.json /path/to/new_course_results
```

The implementation is [course_baseline.py](../research/coldcard/course_baseline.py). It does not modify the historical grouped models or the external model.

## What to explain

“The exercise works on its specified sample. I can read the tree and explain its features. The next question is whether this pattern transfers to groups it has not learned from.”
