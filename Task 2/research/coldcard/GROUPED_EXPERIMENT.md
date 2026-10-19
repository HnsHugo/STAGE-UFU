# Leave-one-candidate-group-out validation

## Data and protocol

The candidate_groups.json file supplied by Hugo exactly matches the 1070 candidate TXIDs in the feature data and the parent report's SHA256. It defines four observed groups of sizes 341, 491, 34 and 204. The fifth source consolidation has no recovered parent in the archive: it does not create a fifth training group.

Each candidate group is reserved for testing once and entirely absent from that fold's training data. Unattributed background is partitioned into four disjoint sets using SHA256(TXID), without using TXID as a predictive feature. Each eligible transaction is therefore evaluated once outside its training set. However, background entities and transitive relationships through missing blocks are unknown: this does not establish independence of all blockchain actors.

Fixed settings: depth 4, at least 20 rows per leaf, class_weight balanced, random_state 42. No tuning to fold scores. Two models: all features and features excluding fee_sat/fee_rate_sat_vb. The 4.95 sat/vB rule remains a descriptive reference previously selected from the data.

## Results by held-out group

| Descendant consolidation, TXID prefix | Candidates | Recovered, full tree | Background alerts, full tree | Recovered, without fees | Background alerts, without fees |
|---|---:|---:|---:|---:|---:|
| 0c6bf853a645 | 341 | 340 | 45 | 341 | 4819 |
| 14edd9ee8445 | 491 | 491 | 911 | 491 | 4845 |
| 38b6dc366fca | 34 | 0 | 47 | 34 | 5951 |
| 4b50d61a3d6e | 204 | 43 | 69 | 43 | 855 |

Alerts on unattributed data are disagreements with a proxy target, not confirmed false positives or newly confirmed thefts.

## Pooled out-of-fold results

| Method | Candidates recovered | Background alerts | Proxy precision | Proxy recall | Proxy F1 |
|---|---:|---:|---:|---:|---:|
| Always background | 0/1070 | 0 | 0% | 0% | 0% |
| One-output rule + fee rate >=4.95 | 1070/1070 | 7231 | 12.89% | 100% | 22.84% |
| Full tree | 874/1070 | 1072 | 44.91% | 81.68% | 57.96% |
| Tree without fees | 909/1070 | 16470 | 5.23% | 84.95% | 9.85% |

Mean recall giving each group equal weight is 55.20% for the full tree, compared with pooled recall of 81.68%. This difference reflects failures on smaller groups: both must be reported, not just the score dominated by larger groups. The full tree's mean per-group F1 is 43.19%.

Weighted tree scores are not calibrated theft probabilities. Pooled average precision combines scores from four distinct trees; interpret it cautiously because scores are not calibrated across folds. Individual results are retained in metrics.json.

## Understanding the differences

Three groups have median fee rates of 30 sat/vB; the group of 34 has a median of 4.9590. Median output amounts also vary: approximately 0.6185 BTC, 0.2510 BTC, 0.0192 BTC and 0.0210 BTC respectively, in table order. The full tree depends strongly on fees and misses the low-fee group. The group of 204 exposes another weakness: removing fees does not restore its recall, which remains 43/204.

These differences document group behaviour within the same case. They do not justify attributing an actor, firmware or wallet model from a transaction alone.

## Reproduction

From Task 2/research/coldcard:

```bash
python -m pip install -r requirements.txt
python train_grouped.py features_output/transactions.csv.gz candidate_groups.json features_output/manifest.json grouped_output
python -m unittest discover -p 'test_*.py' -v
```

The output directory must be new. The feature file is checked against its exact SHA256. Groups are checked against candidate TXIDs, reported counts and parent-report provenance. Different provenance, a missing candidate or a duplicate causes rejection before training.

## Conclusion and next steps

The tree recognizes some candidates and reduces alerts relative to the descriptive rule, but results vary strongly by group. The earlier random-split result (266/267) was more favourable and less independent. Even this improved validation remains internal to one incident and indirect labels.

The useful next step is a sourced label registry with victim/collection/consolidation role, confidence, period and case. Victim addresses must not be confused with illicit addresses; hardware-wallet control must remain an independent property. No Chainabuse report does not constitute a legitimate label. External cases and documented controls are needed before reaching a general conclusion about theft detection.
