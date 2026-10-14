# Validation comparison with 19 reconciled features

The comparison removes transaction_fee_Variance, received_Variance_BTC and sent_Variance_BTC from both training and validation. All remaining 19 base features are kept in the same order. Training-only median imputation adds two missing-sent-extrema indicators (21 transformed columns versus 24 for the original 22-base-feature forest). The source-feature definitions matched seven development training addresses across the prior checks; they are provisionally reconciled, not independently certified for every edge case.

Both forests use 100 trees, maximum depth 20, minimum leaf size 20, sqrt feature sampling, class weight 1 for both classes and seed 42. They reuse the original address split and source files with verified hashes. Source labels remain Hack/Theft versus assumed benign recipients. The baseline reproduces its prior confusion matrix before comparison. The reserved test is not transformed or predicted.

| Validation metric | 22-feature reference | 19-feature alternative |
|---|---:|---:|
| Threshold (strict score >) | 0.15 | 0.15 |
| Precision | 35.53% | 32.58% |
| Recall | 30.92% | 27.48% |
| F1 | 33.06% | 29.81% |
| Average precision | 24.31% | 22.28% |
| True positives | 81 | 72 |
| False positives | 147 | 149 |
| False negatives | 181 | 190 |
| True negatives | 17170 | 17168 |
| Hack recall | 23.94% (34/142) | 21.13% (30/142) |
| Theft recall | 39.17% (47/120) | 35.00% (42/120) |

The fixed previous threshold and best F1 threshold in the original validation grid are both 0.15 for the alternative. F1 declines by 3.25 percentage points; it misses nine additional positives and produces two additional false alerts. Ranking quality also decreases. Removing features changes forest sampling and construction, so this comparison is not proof of the causal contribution of individual variances.

Keep the 22-feature forest as the frozen exploratory offline reference. Retain the 19-feature alternative as a reproducible extraction-compatible development option; it does not improve validation performance. Its schema is simpler to reproduce externally, but external scores would remain descriptive because of limited adapter checks, source label uncertainty, differing observation periods and the tiny case/comparison sample. No EFF/BTCPay score, independent performance claim or final-test result is produced here.

Repeated validation use makes model-selection results optimistic. A larger reviewed case-disjoint evaluation and stronger comparison policy remain necessary. Do not silently remove columns from the original trained model at prediction time; the alternative is trained separately.

## Reproduction

```bash
python compare_reconciled_features.py /path/to/Real-CATS new_validation_report.json
python -m unittest discover -p 'test*.py'
```

The script checks source hashes and baseline reproduction. All threshold-grid metrics and category recalls are stored in reconciled_features_validation_20261014.json. Three existing benchmark tests pass. The next step is a checked adapter for the 19-feature schema, followed by explicitly descriptive external scoring, without retraining against external examples.
