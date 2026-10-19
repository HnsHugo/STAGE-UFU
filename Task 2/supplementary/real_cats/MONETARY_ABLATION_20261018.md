# Monetary feature-family ablation — 18 October 2026

## Hypothesis and protocol

The previous permutation experiment sharply reduced AP by moving amounts without retraining the model. This separate experiment removes the nine features in the `monetary` family and retrains the same configuration to check whether other information can compensate for their removal.

Sources are verified by SHA256, and training/validation memberships match the previous diagnostic: 52,736 / 17,579 addresses. The forest retains 100 trees, maximum depth 20, at least 20 observations per leaf, `max_features=sqrt`, positive class weight 3, and seed 42. The threshold is fixed at a score strictly greater than 0.30, without threshold search. Medians are learned only from the retained training columns. The remaining 13 features contain no missing cells in training/validation.

Removed monetary features are balance, total received/sent amounts, received/sent extrema, and amount variances. Fees remain: this does not remove all financial information. Full lists, parameters, versions, and checksums are saved in `monetary_ablation_20261018.json`.

## Recorded validation results

| Measure | Historical complete forest, no new fitting | Without monetary family, retrained |
| --- | ---: | ---: |
| Average precision | 24.69% | 25.04% |
| Precision | 34.95% | 30.51% |
| Recall | 27.48% | 27.48% |
| F1 | 30.77% | 28.92% |
| Positive references detected | 72 | 72 |
| Positive references missed | 190 | 190 |
| Alerts on the benign category | 134 | 164 |

| Positive category | Historical detections | Detections without amounts |
| --- | ---: | ---: |
| Hack | 33/142 | 24/142 |
| Theft | 39/120 | 48/120 |

## Interpretation

AP without amounts reaches 25.04%, a gain of 0.35 percentage points over the 24.69% reference. This small difference on one seed and one validation set demonstrates neither a statistical improvement nor better generalization.

At the fixed threshold, precision and F1 decrease, with 30 additional alerts on the benign category. Total detections remain 72, but the Hack/Theft distribution changes. Equal totals therefore do not guarantee detection of the same profiles; individual overlap cannot be inferred from aggregates alone.

**Permutation and ablation answer different questions.** The old forest depends on amounts in its learned rules (AP 4.28% after permutation), but a new forest can use other families once amounts are removed. High permutation importance does not establish that the family is irreplaceable after retraining.

## Limitations

The `max_features=sqrt` parameter stays the same, but the effective number of candidate features per split falls from 4 for 22 features to 3 for 13. Removal therefore also changes tree interactions and diversification; the comparison does not measure a unique causal contribution of amounts.

The ablation hypothesis comes from previously inspected validation data: this is a development diagnostic, not a new independent evaluation. No winning model, threshold, or hyperparameter is chosen. The reserved test is neither transformed nor evaluated, and the frozen external model is unchanged. Limitations of source categories, unknown entity/incident groups, and retrospective profiles still apply.

## Reproduction and tests

```bash
python "Task 2/supplementary/real_cats/ablate_monetary_features.py" \
  /path/to/Real-CATS \
  "Task 2/supplementary/real_cats/validation_errors_20261018.json" \
  /path/to/new_results.json
python -m unittest discover -s "Task 2/supplementary/real_cats" -p 'test*.py'
```

At the time of the experiment, all 35 Real-CATS tests passed, including three new tests covering exact family removal, preservation of the original schema, unknown-feature rejection, and per-category counts. Confusion matrices reconcile with the 262 positive references and 17,317 benign-category validation profiles.

## Follow-up proposed at the time

Compare the stability of both configurations across predefined seeds 42, 43, and 44, with unchanged splits and threshold and without choosing a winning seed. Reuse saved seed-42 results when their provenance matches. This algorithmic stability check does not replace independent entity/incident validation. The subsequent result is documented in [SEED_STABILITY_20261018.md](SEED_STABILITY_20261018.md).

Further benchmark development is paused; hardware-wallet case studies are the main priority.
