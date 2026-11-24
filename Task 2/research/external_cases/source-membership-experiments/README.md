# Source-cohort experiment registry

[Current candidate and promotion history](CURRENT.md)

This registry follows the experiments that classify documented Bitcoin source-cohort membership from address histories observed strictly before each reference block. The test population consists of documented sources and same-incident witnesses. Each report records the population, evaluation design and limitations. BTCPay refers to the November 2026 Bitcoin pilot.

## Experiment history

| Date | Experiment | Evidence and outcome |
| --- | --- | --- |
| 2026-11-04 | Frozen Coldcard tree transferred to CryptoBilis | 57 of 122 sources retrieved, with 2 false alerts. Prior inactivity and balance both ranked better by AP on the same 275 observations. [Report](../cryptobilis_frozen_transfer_20261104_215520/README.md) |
| 2026-11-09 | Reverse CryptoBilis to Coldcard transfer | F1 0.9181 on 1,066 eligible observations. The training references follow the test references. [Report](../cryptobilis_to_coldcard_20261109/RESULTS.md) |
| 2026-11-19 | Grouped transfer in both directions | With updated coverage and overlap checks, F1 was 0.5665 for Coldcard → CryptoBilis and 0.9198 in the reverse direction. [Report](../bidirectional_transfer_20261119/RESULTS.md) |
| 2026-11-19 | Grouped within-incident trees | F1 was 0.9832 for Coldcard and 0.9195 for CryptoBilis, using out-of-fold predictions. [Report](../within_incident_20261119/RESULTS.md) |
| 2026-11-19 | Pooled Coldcard + CryptoBilis trees | Global F1 was 0.9376 under grouped validation. [Report](../pooled_incidents_20261119/RESULTS.md) |
| 2026-11-24 | Held-out BTCPay pilot | Five frozen trees were applied to 38 eligible observations. Four retrieved zero sources and one retrieved two. [Report](experiments/2026-11-24-btcpay-frozen.md) |
| 2026-11-24 | Three-incident matrix | 49 configurations include 12 external, 19 internal and 18 mixed cells. Inactivity ranked ahead of the main tree in all nine single-target external transfers. [Report and complete data](https://github.com/HnsHugo/STAGE-UFU/blob/947a8ae25c8d720dec90c69e267dd2b3bff7d4ea/Task%202/research/external_cases/incident_test_matrix/run-3ffacb2f8b1c982d/README.md) |
| 2026-11-24 | Inactivity thresholds selected for training F1 | The rule outperformed both trees in seven of nine external transfers and tied the best tree in two. [Report and complete data](experiments/2026-11-24-inactivity-threshold.md) |
| 2026-11-24 | Activity-feature ablation | Removing activity features changes the opening split toward balance. Average transfer F1 declines for the main tree and rises modestly for the smaller tree. [Report and complete data](experiments/2026-11-24-activity-ablation.md) |
| 2026-11-24 | Logistic regression and false-alert budget | Inactivity plus balance is the current candidate for further validation. It improves Coldcard → CryptoBilis at fewer false alerts, with weaker results on BTCPay. [Report and complete data](experiments/2026-11-24-logistic-false-alert-budget.md) |
| 2026-11-24 | Fourteen methods across the 49-cell matrix | Compared simple rules, trees, logistic variants, forest, boosting, Gaussian naive Bayes and RBF SVM. On Coldcard → CryptoBilis, Gaussian naive Bayes retrieves 109 of 122 sources with 4 false alerts. Inactivity has the best mean external AP. [Report and complete data](experiments/2026-11-24-method-benchmark.md) |
| 2026-11-25 | Bitfinex 2016 retrospective pilot | The frozen Coldcard inactivity rule retrieved 3 of 5 sources with zero false alerts. Five of the 14 methods retrieved 4 sources with 1 false alert. [Report](experiments/2026-11-25-bitfinex-retrospective.md) |

## Maintaining the registry

Add a dated entry for every completed comparison, including failures and inconclusive results. Link its verified aggregate report and record the test population, design, outcome and applicable limits. Keep the earlier records and their stable links.

When a comparison supports changing the current candidate, update the link in [CURRENT.md](CURRENT.md) and append the date, decision, evidence and previous candidate. Compare on identical external observations and look for more retrieved sources at the same or lower number of false alerts. Report whether the realized false-alert rate meets the 5% target and give greater weight to a previously untouched incident evaluated in chronological order. The three current incidents have already been inspected.

The registry contains aggregate results and methods. Raw histories, address-level labels, predictions, identifiers and collection records are stored privately.
