# Descriptive validation error analysis

## Scope

This analysis examines the already selected development model: full-profile depth-8 tree, minimum leaf size 20, illicit class weight 3, and score >0.75. It reproduces the original training/validation split and evaluates validation only. No test evaluation, threshold change or new configuration is introduced.

The target remains the original offline Elliptic++ illicit/licit label, not theft attribution or real-time detection. Findings are descriptive associations within reused validation data, not causal explanations or independent validation.

## Error counts

Validation contains 53,071 addresses. There are 1,701 true positives, 402 false positives, 1,152 false negatives and 49,816 true negatives. Precision is 80.88%, recall 59.62%, and F1 68.64%.

## Errors concentrated in particular leaves

| Leaf | True positives | False positives | False negatives | True negatives | Weighted score |
| --- | ---: | ---: | ---: | ---: | ---: |
| 119 | 878 | 159 | 0 | 0 | 0.9540 |
| 149 | 407 | 142 | 0 | 0 | 0.9081 |
| 134 | 0 | 0 | 291 | 1974 | 0.3280 |
| 68 | 0 | 0 | 200 | 1691 | 0.2233 |
| 15 | 0 | 0 | 159 | 1511 | 0.2319 |

Two leaves (119 and 149) account for 301/402 false positives, or 74.88%. They also recover 1,285 illicit-labeled addresses. Raising a global threshold enough to reject these leaves would therefore discard many correct alerts as well. A score is shared by every address reaching the same leaf; it cannot distinguish the licit and illicit examples within that leaf.

Three leaves (134, 68 and 15) account for 650/1152 false negatives, or 56.42%. They contain many licit examples alongside the missed illicit ones. Lowering the global threshold enough to recover these whole leaves would introduce substantial additional alerts.

Full conditions and raw training support for the five largest FP/FN leaves are in validation_errors_20261013/error_analysis.json. Leaf 119 has 3,104 training examples, of which 2,712 are illicit (87.37% unweighted), but its class-weighted score is 95.40%. Leaf 149 has 1,589 training examples, 1,219 illicit (76.71% unweighted), and a weighted score of 90.81%. These errors are not limited to tiny leaves, and weighted scores must not be read as calibrated probabilities.

## Profile comparisons

The following are medians over each validation error group. They are descriptive summaries, not single-variable classification rules.

| Feature | Correct illicit alerts (TP) | False alerts (FP) | Missed illicit addresses (FN) | Correct licit decisions (TN) |
| --- | ---: | ---: | ---: | ---: |
| total_txs | 2 | 2 | 1 | 1 |
| btc_sent_mean | 0.003999 | 0.011095 | 0.009578 | 0 |
| btc_received_total | 0.006600 | 0.019741 | 0.006840 | 0.000288 |
| fees_max | 0.022352 | 0.024248 | 0.000946 | 0.001889 |
| blocks_btwn_txs_mean | 1 | 2 | 0 | 0 |
| transacted_w_address_total | 2 | 2 | 2 | 2 |

TP and FP groups have the same median transaction count and similar median maximum fee values. FN and TN groups share a median transaction count of 1 and a median inter-transaction interval of 0. These summaries are consistent with overlapping profiles but do not establish irreducible overlap or the causes of individual errors. A zero interval must not automatically be interpreted as inactivity or a wallet-owner decision. Dataset fee features must not be assumed to represent fees paid solely by the address's owner.

## Are errors near the threshold?

In the diagnostic score band (0.65, 0.85], there are 39 TP, 27 FP, 24 FN and 66 TN. Only 24/1152 missed illicit addresses lie in that band below the current threshold, and only 27/402 false alerts lie in it above the threshold. A modest threshold adjustment therefore cannot correct most existing errors. This band was chosen for diagnosis after threshold selection; it is not a new operating rule.

## Next experiment

Compare an ensemble with the same training/validation protocol to test whether more flexible partitions separate these mixed leaves better. Report validation tradeoffs rather than assuming an improvement. Retain the current tree as an interpretable reference. Verify feature semantics and, for the final project, reconstruct decision-time features and acquire independent case-level evidence. This diagnostic analysis has reused validation; independent confirmation is still required.

## Reproduction

```bash
python analyze_validation_errors.py /path/to/ellipticplusplus /path/to/new_error_output
```

The script checks the input hashes, reproduces the selected tree and exports group quantiles, leaf paths, training support and near-threshold counts. The output directory must be new. Identifiers and individual address examples are not published in this report; all outputs are aggregate diagnostics.
