# Missingness-only baselines — 18 October 2026

## Hypothesis and predefined protocol

The previous diagnostic showed that missing-value frequency differed across source categories. This experiment checks the ranking ability of those indicators alone, without seeking to improve the existing model.

The SHA256-verified corpus, 52,736 training observations, and 17,579 validation observations match the previous diagnostic; split-membership checksums are verified. No predictive content from the reserved test is transformed or evaluated.

Each of the 22 original numerical features is replaced with a binary indicator: 1 for missing, nonnumeric, or nonfinite values, and 0 otherwise. The numerical values themselves are never supplied to the models. No imputation is needed.

Three baselines were predefined: a constant score equal to training prevalence; an unweighted tree with maximum depth 2 and at least 20 observations per leaf; and the same tree using balanced weights calculated on training. Seed 42 is used, and splits are learned on training only. All use the strict threshold >0.5. No model, threshold, or hyperparameter is selected from this validation.

## Recorded results

| Model | Average precision | Precision | Recall | F1 | Positive references detected | Alerts on the benign category |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Constant score | 1.49% | 0.00% | 0.00% | 0.00% | 0/262 | 0 |
| Missingness only, unweighted | 1.75% | 0.00% | 0.00% | 0.00% | 0/262 | 0 |
| Missingness only, balanced weights | 1.75% | 1.75% | 98.85% | 3.45% | 259/262 | 14501 |
| Historical numerical forest, threshold 0.30 | 24.69% | 34.95% | 27.48% | 30.77% | 72/262 | 134 |

Comparison of operating points must account for the different thresholds and weights: 0.5 for the new baselines, and the previously selected 0.30 for the forest. Average precision compares rankings without choosing a new threshold. As expected, the constant score obtains positive validation prevalence.

## Interpretation

Missingness alone slightly improves ranking over the constant score but does not reproduce the numerical forest's performance. No causal collection or source effect is established.

Two missingness patterns occur in training and validation, with no new pattern in validation. In the validation diagnostic, all missing cells concern `max_sent_amount` and `min_sent_amount`. Both trees use a single split on `missing__max_sent_amount`; their full rules are saved in the JSON. With balanced weights, no missingness produces an alert and missingness produces no alert. Without weighting, both leaves predict the negative class at the fixed threshold, while assigning two distinct ranking scores.

These missing values may reflect no sending activity, a feature definition, or collection practices. Their cause has not been verified. The simultaneous presence of both indicators prevents assigning an independent effect to either one.

Balanced weights flag 14,760 profiles, including 14,501 in the benign category: very high recall does not demonstrate a useful detector. Categories come from Real-CATS, without independent evidence of victim/attacker roles. Entity/incident relationships remain unknown, profiles are retrospective, and scores are not calibrated theft probabilities.

This study uses previously inspected validation data and remains a development diagnostic. It demonstrates neither external generalization gains nor the absence of source bias. The historical forest is not retrained in this unit, and the frozen external model remains intact.

## Reproduction and tests

```bash
python "Task 2/supplementary/real_cats/compare_missingness_baselines.py" \
  /path/to/Real-CATS \
  "Task 2/supplementary/real_cats/validation_errors_20261018.json" \
  /path/to/new_results.json
python -m unittest discover -s "Task 2/supplementary/real_cats" -p 'test*.py'
```

Saved output: `missingness_baselines_20261018.json`. The script refuses to overwrite an existing result. At the time of the experiment, all 29 Real-CATS tests passed, including four new tests covering removal of numerical values, nonfinite-value conversion, the constant baseline, and the strict threshold boundary.

## Follow-up proposed at the time

Study permutation importance for feature families in the historical numerical forest, using validation only, average precision, and a seed and repetition count fixed before execution. Group strongly related features before permutation to limit artificial combinations; document that permutation importance is not a causal explanation. Do not select new parameters on the reserved test. The subsequent result is documented in [GROUPED_PERMUTATION_20261018.md](GROUPED_PERMUTATION_20261018.md).

Further benchmark development is paused; hardware-wallet case studies are the main priority.
