# Real-CATS validation-error diagnostic — 18 October 2026

## Experiment performed

This diagnostic reproduces the historical benchmark forest with **22 features**, positive class weight 3, 100 trees, maximum depth 20, at least 20 observations per leaf, `max_features=sqrt`, and seed 42. The historical threshold remains strictly greater than 0.30. This model is separate from the frozen external 19-feature forest with threshold 0.15, which is neither changed nor run.

The BB.tsv and CB.tsv sources are verified against their original checksums. The same addresses and splits are reconstructed: 52,736 training rows and 17,579 validation rows. Median imputation is learned on training only. Only the previously saved parameters are refitted, because no historical fitted model had been exported. Reserved-test features and predictions are neither transformed nor calculated.

Before the diagnostic, all eight validation metrics are compared against historical values with an absolute tolerance of 1e-12. Reproduction succeeds: precision 34.95%, recall 27.48%, F1 30.77%, and average precision 24.69%. The confusion matrix is TP=72, FN=190, FP=134, TN=17,183, relative to source categories.

## Categories and missing values before imputation

| Source category | Profile | Count | Alerts | Alert rate |
| --- | --- | ---: | ---: | ---: |
| benign | All | 17317 | 134 | 0.77% |
| benign | No missing values | 14501 | 131 | 0.90% |
| benign | At least one missing value | 2816 | 3 | 0.11% |
| Hack | All | 142 | 33 | 23.24% |
| Hack | No missing values | 141 | 33 | 23.40% |
| Hack | At least one missing value | 1 | 0 | 0.00% |
| Theft | All | 120 | 39 | 32.50% |
| Theft | No missing values | 118 | 39 | 33.05% |
| Theft | At least one missing value | 2 | 0 | 0.00% |

For Hack and Theft, the alert rate is category recall; for benign, it is the rate of disagreement with its negative label. The “All” rows include both subgroups: do not add all three rows.

## Findings and limitations

**187 of the 190 missed positives have no missing values.** Adding missingness indicators alone therefore cannot be presented as a demonstrated fix for low recall. All three incomplete positive profiles are missed, but this count is too small to generalize.

Missingness is much more frequent in the benign category (2,816/17,317) than among Hack/Theft references (3/262). This association may reflect behavior, feature definitions, or source collection; the diagnostic does not distinguish these explanations. It motivates a missingness-only baseline to assess a possible source shortcut, without concluding that missingness causes the errors.

For each feature and each TP/FN/FP/TN outcome, the JSON also retains the number of missing cells before imputation. It publishes neither a list of accused addresses nor individual scores. Missingness patterns and rates are descriptive, without a causal test, SHAP attribution, or population-performance estimate.

Validation was already used for historical model and threshold selection. This diagnostic is therefore not a new independent evaluation. Entity/incident groups remain unknown, source categories do not verify victim/attacker roles, and full-lifetime profiles remain retrospective. No threshold or hyperparameter is selected from these results.

## Reproduction and checks

From the repository root, with dependencies from `Task 2/supplementary/real_cats/requirements.txt` and a new output path:

```bash
python "Task 2/supplementary/real_cats/analyze_validation_errors.py" \
  /path/to/Real-CATS \
  "Task 2/supplementary/real_cats/results_20261013/metrics.json" \
  /path/to/new_diagnostic.json
python -m unittest discover -s "Task 2/supplementary/real_cats" -p 'test*.py'
```

The recorded output is `validation_errors_20261018.json`. It contains library versions, parameters, features, and checksums for the sources, historical report, and training/validation memberships. At the time of the experiment, all 25 Real-CATS tests passed, including three new tests covering subgroup consistency, absent categories, and invalid inputs.

## Follow-up proposed at the time

Compare a baseline using only missingness indicators against constant baselines, on training/validation only, with configuration fixed before execution. This source-shortcut diagnostic must retain all its metrics, without adjusting the external model or using the reserved test. The subsequent result is documented in [MISSINGNESS_BASELINES_20261018.md](MISSINGNESS_BASELINES_20261018.md).

Further benchmark development is paused; hardware-wallet case studies are the main priority.
