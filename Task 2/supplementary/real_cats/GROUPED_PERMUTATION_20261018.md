# Feature-family permutation importance — 18 October 2026

## Experiment performed

This experiment measures the historical 22-feature forest's dependence on four feature families defined before computation. It refits only the historical configuration on the 52,736 training profiles, then uses the 17,579 validation profiles. Imputation medians are learned on training only. Checksums for both sources and split memberships are verified. The reserved test set is neither transformed nor evaluated.

The reference average precision (AP), 24.6924526106%, is reproduced within an absolute tolerance of 1e-12. No threshold is selected: AP measures the ranking of positive references among validation profiles.

Four families cover every feature exactly once: amounts/balance (9), activity counts (7), time/temporal activity (4), and fees (2). Exact lists are saved in the JSON. Each family is moved jointly using a row permutation, while the other columns remain fixed. After imputation using fixed statistics, this operation preserves the family's joint values, including medians substituted for missing values.

Five permutations are drawn using `numpy.default_rng(42)` and reused across all families to limit comparison variability. A control moves all 22 features together: it preserves each joint profile but separates it from its label. All 25 perturbed AP scores, five permutation checksums, and library versions are recorded.

## Recorded results

| Perturbed family | Mean AP after permutation | Mean AP decrease (percentage points) | Standard deviation of decrease (percentage points) |
| --- | ---: | ---: | ---: |
| Amounts and balance | 4.28% | 20.41 | 0.47 |
| Activity counts | 7.88% | 16.82 | 0.77 |
| Duration and temporal activity | 11.15% | 13.55 | 0.61 |
| Fees | 12.56% | 12.13 | 0.91 |
| Control: all features together | 1.64% | 23.05 | 0.15 |

The global control obtains mean AP of 1.64%, close to positive validation prevalence (1.49%). Differences across its five repetitions are retained; they do not form a population confidence interval.

## Interpretation and limitations

Perturbing amounts produces the largest ranking decrease among these predefined families. Activity counts, temporal features, and fees also show substantial decreases. This complements the previous baseline: missingness alone did not explain the numerical forest's performance.

**The decreases must not be added or converted into contribution shares.** Families differ in size and interact; information may be redundant. Their ranking is therefore not an intrinsic ranking of individual features.

The shared permutation preserves relationships within the moved family but may break dependencies between families: moved amounts may no longer match the activity counts or fees in their new row. The measure describes model dependence under this perturbation, not causal importance or an independent contribution. It does not replace ablation with retraining.

Row permutations do not account for unknown entity/incident groups. Full-lifetime profiles remain retrospective, and source categories do not certify victim/attacker roles. Validation was already used to select the model; this remains a development diagnostic. The external 19-feature model and its 0.15 threshold are preserved.

## Reproduction and tests

```bash
python "Task 2/supplementary/real_cats/grouped_permutation_importance.py" \
  /path/to/Real-CATS \
  "Task 2/supplementary/real_cats/validation_errors_20261018.json" \
  /path/to/new_results.json
python -m unittest discover -s "Task 2/supplementary/real_cats" -p 'test*.py'
```

The recorded output is `grouped_permutation_20261018.json`. At the time of the experiment, all 32 Real-CATS tests passed, including three new tests covering joint dependencies, unchanged input data, identity permutation, duplicate rejection, and schema coverage.

## Follow-up proposed at the time

Compare an ablation without the amount family against the complete configuration on training/validation, using the same parameters and a threshold fixed before computation. This separates perturbation of an already fitted model from its ability to relearn using other families. Do not select parameters using the reserved test or present validation as independent. The subsequent result is documented in [MONETARY_ABLATION_20261018.md](MONETARY_ABLATION_20261018.md).

Further benchmark development is paused; hardware-wallet case studies are the main priority.
