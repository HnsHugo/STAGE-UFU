# Real-CATS validation errors and missing-data analysis

## Protocol

This descriptive analysis recreates the selected forest with the original settings and threshold >0.30: 100 trees, depth 20, minimum leaf size 20, positive class weight 3, seed 42. Imputation is fitted only to original training rows. Only training and validation feature values are inspected; no test predictions or threshold selection are performed. All baseline validation metrics are checked to reproduce the saved experiment to numerical tolerance.

## Category-specific errors

| Source category | Validation addresses | Alerted | Not alerted | Alert rate |
| --- | ---: | ---: | ---: | ---: |
| Hack | 142 | 33 | 109 | 23.24% recall |
| Theft | 120 | 39 | 81 | 32.50% recall |
| benign | 17317 | 134 | 17183 | 0.77% false-alert rate |

Pooled validation precision is 34.95%, recall 27.48% and F1 30.77%. The model detects Theft references more often than Hack references in this particular validation sample; case IDs and independent source-role verification are unavailable, so this does not establish a universal difference between incident types.

## Missing values have a specific meaning

There are 16,818 missing numeric cells in training and 5,638 in validation. Validation missing values occur only in max_sent_amount and min_sent_amount, for 2,819 addresses. Every one of those addresses has payment_transactions=0. The unavailable sent-amount extrema therefore coincide with no observed outgoing transaction, rather than arbitrary missing financial fields.

Of these validation addresses, 2,816 are benign, 1 Hack and 2 Theft. Median imputation replaces unavailable extrema with a numeric value learned from training; that replacement is not an observed outgoing payment. An explicit no-outgoing/missing indicator is a reasonable preprocessing comparison, but may also reflect the dataset's comparison-selection policy.

| Validation group | Addresses | Addresses with missing features |
| --- | ---: | ---: |
| Correct positive alerts (TP) | 72 | 0 |
| False alerts (FP) | 134 | 3 |
| Missed positive references (FN) | 190 | 3 |
| Correct benign decisions (TN) | 17183 | 2813 |

Only 3/190 missed positive references and 3/134 false alerts have missing features. Missingness cannot directly account for most errors. Training imputation can also influence fitted partitions, so these counts do not prove it has no indirect effect.

## Profiles overlap in simple counts

| Median feature | TP | FP | FN | TN |
| --- | ---: | ---: | ---: | ---: |
| transaction_number | 2 | 2 | 2 | 2 |
| payment_transactions | 1 | 1 | 1 | 1 |
| receipt_transactions | 1 | 1 | 1 | 1 |
| received_counters | 2 | 2 | 2 | 3 |
| lifetime, seconds | 200845 | 132030 | 514907 | 1110381 |
| transaction_fee, source units | 44479.91216 | 30627 | 20691.75 | 9042.3 |

These are descriptive medians, not causal explanations or single-feature detection rules. The same typical transaction counts appear across all error groups. Lifetime and fee distributions differ in their medians, but summaries do not establish separability. Whole-history source features do not describe a decision-time observation window, and source fee summaries must not be interpreted as an address owner's independent fee policy without tracing transactions.

## Score distribution and threshold limits

Median scores are about 0.1144 for Hack, 0.2097 for Theft and 0.0107 for benign. In the diagnostic band (0.20, 0.40], there are 34 TP, 100 FP, 43 FN and 260 TN. Only 43/190 missed positives are immediately below the current threshold in that band, while 47/190 have scores below 0.05. Simply moving the threshold slightly cannot recover most missed positives; lowering it also alerts many benign profiles.

The band is descriptive and was chosen after examining the selected model. It is not a new operating threshold. Existing model settings and historical test metrics remain unchanged.

## Recommended next development comparison

1. Compare training-only median imputation with explicit missing/no-outgoing indicators; do not assume that correcting missing-data representation will fix low recall.
2. Compare a small predefined class-weight grid and validation threshold tradeoffs, reporting Hack and Theft recall separately.
3. Diagnose source provenance, observation-period and comparison-population effects. Better partitions or richer graph features are hypotheses to test, not established solutions.

All choices must be made on training/validation. The already inspected test must not guide tuning; independent confirmation is still required. Categories remain source assertions, not independently verified stolen-fund roles.

## Reproduction

```bash
python analyze_validation.py /path/to/Real-CATS results_20261013/metrics.json /path/to/new_analysis_output
python -m unittest discover -p 'test_*.py' -v
```

The output directory must be new. Input SHA-256 checksums are verified and baseline validation is reproduced before diagnostics are written. analysis_20261014/validation_analysis.json retains category and error-group quantiles, missingness counts, training imputation medians and feature importances. No individual address examples are published in this analysis. Three source-category tests pass.
