# Part 3 — Reproduce the professor's classroom classifier

[Previous: Part 2](../part_2_dataset/README.md) · [Main path](../README.md) · [Next: Part 4](../part_4_validation/README.md)

## Goal

Implement the course exercise: 100 transactions paying the course address, 100 comparisons and an interpretable decision tree.

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
