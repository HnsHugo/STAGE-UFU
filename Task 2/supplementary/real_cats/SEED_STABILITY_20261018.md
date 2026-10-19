# Algorithmic stability across three seeds — 18 October 2026

## Protocol performed

Seeds 42, 43, and 44 were fixed before this experiment for the complete 22-feature forest and the 13-feature variant without the monetary family. The same 52,736 training rows and 17,579 validation rows are used. Only the forest's `random_state` changes; split seeds remain unchanged.

Seed-42 results are reused after checking source checksums, split memberships, the reference report, library versions, features, threshold, and parameters. Only four new forests are fitted: two configurations for seeds 43 and 44. Both imputers are learned on training only, then reused across seeds.

Parameters remain unchanged: 100 trees, maximum depth 20, at least 20 rows per leaf, `max_features=sqrt`, positive class weight 3, and strict threshold >0.30. The caveat about the effective number of candidate features per split (4 versus 3) still applies. No model or seed is selected, and the reserved test is neither transformed nor evaluated.

## Results by seed

| Seed | Complete AP | AP without amounts | Complete F1 | F1 without amounts | Detections, complete / without amounts | Benign alerts, complete / without amounts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 24.69% | 25.04% | 30.77% | 28.92% | 72 / 72 | 134 / 164 |
| 43 | 25.04% | 24.86% | 29.67% | 27.85% | 73 / 66 | 157 / 146 |
| 44 | 23.52% | 25.74% | 29.75% | 28.45% | 72 / 69 | 150 / 154 |

## Descriptive summaries

| Measure | Complete: mean ± standard deviation | Without amounts: mean ± standard deviation |
| --- | ---: | ---: |
| Average precision | 24.42% ± 0.65 percentage points | 25.21% ± 0.38 percentage points |
| Precision | 33.04% ± 1.38 percentage points | 30.86% ± 0.26 percentage points |
| Recall | 27.61% ± 0.18 percentage points | 26.34% ± 0.93 percentage points |
| F1 | 30.07% ± 0.50 percentage points | 28.41% ± 0.44 percentage points |

Standard deviations use `ddof=0` and describe only these three seeds. They are neither standard errors nor confidence intervals for population performance. The seeds share exactly the same data and do not constitute three independent test sets.

## Interpretation

The mean AP difference, without amounts minus complete, is +0.79 percentage points, but ranges from -0.18 to +2.21 points and changes sign. It does not demonstrate a robust or statistically significant gain. At the shared threshold, the variant without amounts has lower F1 on all three seeds; its precision is also lower on each. These observations do not justify replacing the historical model.

Retraining without amounts can still produce a ranking close to that of the complete model, consistent with information redundancy. This conclusion establishes neither a unique causal contribution nor independence from sources.

This study uses a fixed, previously inspected validation set. It does not measure variability across splits, data, entities, or incidents. Source categories and full-lifetime profiles retain their role and temporal limitations. The external 19-feature forest and its 0.15 threshold remain preserved.

## Reproduction and tests

```bash
python "Task 2/supplementary/real_cats/check_seed_stability.py" \
  /path/to/Real-CATS \
  "Task 2/supplementary/real_cats/validation_errors_20261018.json" \
  "Task 2/supplementary/real_cats/monetary_ablation_20261018.json" \
  /path/to/new_results.json
python -m unittest discover -s "Task 2/supplementary/real_cats" -p 'test*.py'
```

Output: `seed_stability_20261018.json`, including metrics and categories for each seed, paired statistics, versions, and provenance for both caches. At the time of the experiment, all 39 Real-CATS tests passed, including four new tests covering seed coverage, paired differences, the dispersion definition, and rejection of a cache with a modified threshold.

## Follow-up proposed at the time — paused

Introduce a regularized logistic-regression baseline with preprocessing and parameters fixed before execution and learned on training only. Compare validation AP rankings against saved references, without threshold search or selection on the reserved test. This other model family would add more information than indefinitely extending the seed search.

This proposal has not been executed as part of this report. Further benchmark development is paused; hardware-wallet case studies are the main priority.
