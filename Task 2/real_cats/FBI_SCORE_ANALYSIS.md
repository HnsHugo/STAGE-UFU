# Why three FBI-attributed addresses remain below the fixed threshold

The fixed 19-feature forest is refitted solely on the original training split with unchanged settings. All six FBI scores reproduce the prior values within 1e-12. Validation/test predictions and threshold tuning are not performed.

| Address | Score | Gap to fixed threshold 0.15 | Spending transactions | Total transactions | Active UTC days |
|---|---:|---:|---:|---:|---:|
| 3LU8wRu4ZnXP4UM8Yo6kkTiGHM9BubgyiG | 0.118753 | -0.031247 | 2 | 5 | 4 |
| 3PjNaSeP8GzLjGeu51JR19Q2Lu8W2Te9oc | 0.148067 | -0.001933 | 2 | 4 | 3 |
| 39idqitN9tYNmq3wYanwg3MitFB5TZCjWu | 0.143064 | -0.006936 | 2 | 4 | 3 |
| 34VXKa5upLWVYMXmgid6bFM4BaQXHxSUoL | 0.233841 | +0.083841 | 1 | 3 | 2 |
| 3AAUBbKJorvNhEUFhKnep9YTwmZECxE4Nk | 0.236503 | +0.086503 | 1 | 3 | 2 |
| 3NbdrezMzAVVfXv5MTQJn4hWqKhYCTCJoB | 0.225124 | +0.075124 | 1 | 3 | 2 |

## Observed differences

All three below-threshold addresses have two spending transactions versus one for each above-threshold address. Their total transaction counts are 4–5 versus 3 and active-day counts 3–4 versus 2. These are correlated observations within one grouped case, not independent predictors or a rule that two spends imply legitimacy. Received-value ranges overlap strongly; some below-threshold addresses receive more than some above-threshold addresses. Large balances or amounts alone do not guarantee a flag.

Two scores are close to the threshold. This describes sensitivity to the operating threshold; it is not permission to lower it after inspecting these external examples. A missing flag means below the chosen score threshold, not a model-certified legitimate address.

## Exact tree-path accounting

For each tree, the positive-class proportion at the root forms a baseline. Following the address down the tree, every child-minus-parent proportion change is attributed to that split feature. Averaging the baseline and feature changes across the forest reconstructs the score exactly. Additivity is asserted within 1e-12 for all six addresses. The common mean root baseline is 0.014907274.

This is tree-path accounting, not SHAP. Contributions depend on split order, feature correlations and tree construction. They do not establish causality, criminality or the score effect of a valid counterfactual address. No feature-importance ranking is substituted for a local explanation.

The strongest mean contribution difference between above/below groups comes from max_received_amount: +0.03675 versus +0.01604, a score gap contribution of about 0.02071. sent_counters and received_counters contribute mean differences of about 0.01238 and 0.01170. These are how the existing trees allocate score along their paths, not isolated effects of changing those columns. In particular, similar counter values can have different contributions because addresses traverse different earlier splits.

For 3LU8w..., receipt_transactions contributes -0.00486 and lifetime -0.00364. Most contributions are positive relative to the low root baseline, but they do not raise the overall score enough to cross 0.15. For the two near-threshold addresses, receipt_transactions contributes about -0.00299. Complete signed contributions for every transformed feature are stored in fbi_path_explanations_20261014.json.

## Consequence

The pilot shows a mismatch between the Real-CATS source-category classifier and some officially attributed stolen-funds holders. Full-history features include later spending and cannot demonstrate early detection at the FBI publication date. The six addresses remain one conservative incident group, and evidence roles differ from training labels. Do not tune the model on this group or report a general false-negative rate from six examples.

Keep settings frozen. The next evidence improvement is additional documented comparison entities and independent case groups under a fixed observation policy. Any future model change should be developed on training/validation data, followed by a new independently reserved evaluation.

## Reproduction

```bash
python explain_fbi_paths.py /path/to/Real-CATS expanded_external_scores_20261014.json new_fbi_explanations.json
python -m unittest discover -p 'test*.py'
```

Source hashes, fixed-score reproduction and exact decomposition are checked on real inputs. Three benchmark tests pass. No model changes, external fitting or messages to third parties occur.
