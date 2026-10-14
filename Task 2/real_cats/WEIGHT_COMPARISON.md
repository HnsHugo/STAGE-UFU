# Validation class-weight and missingness comparison

Six preset random forests reuse the original address split and verified source files. Training-only median imputation is used, optionally adding two indicators (maximum/minimum sent amount). The reserved test is never transformed or predicted. All forests retain 100 trees, depth 20, minimum leaf size 20, sqrt feature sampling, and seed 42. Each candidate uses the original threshold grid and strict score > threshold rule, selecting its highest validation F1.

| Positive weight | Missing indicators | Threshold | Precision | Recall | F1 | TP | FP | Hack recall | Theft recall |
|---|---|---|---|---|---|---|---|---|---|
| 1 | False | 0.15 | 33.33% | 29.77% | 31.45% | 78 | 156 | 24.65% | 35.83% |
| 3 | False | 0.30 | 34.95% | 27.48% | 30.77% | 72 | 134 | 23.24% | 32.50% |
| 10 | False | 0.45 | 30.94% | 32.82% | 31.85% | 86 | 192 | 23.94% | 43.33% |
| 1 | True | 0.15 | 35.53% | 30.92% | 33.06% | 81 | 147 | 23.94% | 39.17% |
| 3 | True | 0.25 | 30.13% | 34.73% | 32.27% | 91 | 211 | 27.46% | 43.33% |
| 10 | True | 0.40 | 26.29% | 38.93% | 31.38% | 102 | 286 | 30.99% | 48.33% |

The validation F1 winner is weight 1 with indicators: TP 81, FP 147, FN 181, TN 17170. Relative to the reproduced weight-3 baseline, it gains nine detections and adds thirteen false alerts; F1 increases by 2.29 percentage points. Hack detection changes from 33/142 to 34/142, while Theft changes from 39/120 to 47/120. Most positives remain missed.

Average precision does not improve: the baseline is 0.2469 and the F1 winner is 0.2431. This is a modest threshold-dependent validation gain, not clear evidence of better ranking. Higher weights trade precision for recall; weight 10 with indicators detects 102 positives but generates 286 false alerts.

Repeated validation selection is optimistic. These results do not establish an independent test improvement or justify retuning against the already inspected test. The next confirmation requires a separately reserved dataset or case-aware evaluation with trustworthy labels. Source Hack/Theft reports and assumed benign recipients are not independently verified incident roles; full-history features remain an offline benchmark. Scores are not calibrated probabilities.

## Reproduction

```bash
python compare_validation_weights.py /path/to/Real-CATS /path/to/new-output
python -m unittest discover -p "test*.py"
```

Input checksums are checked. A runtime guard reproduces the baseline validation confusion matrix exactly (72 TP, 134 FP, 190 FN, 17183 TN). The existing three source-preparation tests pass. Complete threshold grids are stored in weights_20261014/metrics.json.
