# Sent-variance investigation and validation ablation

The original Real-CATS repository tree was inspected through the GitHub API on 14 October 2026 at revision 054c659412a07d1dac596f625d02a84039f22a9b. The recursive response was not truncated. Its ten paths contain data tables, README and license, with no extractor. Searches of the repository, author profile and exact feature name did not locate original extraction code. The linked Kaggle page did not expose file descriptions in the retrieved text; its contents were not inspected, so this is not proof that no extractor exists anywhere. Evidence is recorded in sent_variance_investigation_20261014.json.

For the two nonzero training discrepancies, population/sample variance of individual own input slots and population/sample variance of per-outgoing-transaction aggregate amounts were computed. None explains both published rows within the same disclosed rounding tolerance. The one-spend Theft reference has nonzero source variance, excluding per-transaction variance as a general explanation. This does not prove a source bug: undisclosed running statistics, omitted conventions or source-record differences remain possible. Do not assert a recovered original formula.

## Controlled development comparison

Two forests retain the prior weight-1 missing-indicator configuration, original training/validation split, seed 42, 100 trees, depth 20, minimum leaf size 20 and sqrt feature sampling. Only sent_Variance_BTC is removed in the alternative. Median imputation and missingness indicators are fitted on training only. Both use the same original threshold grid; the baseline reproduces 81 TP and 147 FP at score > 0.15. No reserved-test feature transformation or prediction occurs.

| Validation configuration | Threshold | Precision | Recall | F1 | Average precision | TP | FP |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original 22 features | 0.15 | 35.53% | 30.92% | 33.06% | 24.31% | 81 | 147 |
| Remove sent variance, fixed original threshold | 0.15 | 33.96% | 27.48% | 30.38% | 25.06% | 72 | 140 |
| Remove sent variance, best validation grid threshold | 0.10 | 24.60% | 40.84% | 30.70% | 25.06% | 107 | 328 |

At its best F1 threshold the alternative detects more positives but generates 181 extra false alerts relative to the baseline. Average precision improves by about 0.75 percentage points, while best F1 declines by 2.36 points. These metrics describe different aspects; they do not support a blanket improvement claim. Dropping one column also changes feature sampling and forest construction, so this is a configuration comparison, not causal attribution to that feature alone. Repeated validation use makes estimates optimistic.

Keep the original model as the frozen exploratory benchmark. The 21-feature alternative is not independently confirmed and does not automatically authorize external scoring: remaining fee-variance, missing-direction, self-transfer and script-counterparty edge cases still need reference checks. No EFF/BTCPay scores or verified-theft detection metrics are produced. Obtaining the source extractor would resolve the remaining ambiguity; no message or issue was sent to the authors.

## Reproduction

```bash
python compare_sent_variance_ablation.py /path/to/Real-CATS new_ablation_report.json
python -m unittest discover -p 'test*.py'
```

Source hashes and baseline reproduction are enforced. All threshold metrics and per-category recall are recorded in sent_variance_ablation_20261014.json. The three existing benchmark tests pass. Mathematical candidates are recorded separately so the unresolved feature is reviewable.
