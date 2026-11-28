# Most promising experiment

**Current candidate, 2026-11-24:** [Logistic regression on prior inactivity and balance](experiments/2026-11-24-logistic-false-alert-budget.md#coldcard-to-cryptobilis).

On the chronological Coldcard → CryptoBilis transfer, the candidate retrieves **100 of 122 sources with 6 false alerts**, compared with **60 of 122 with 7 false alerts** for prior inactivity alone. Both methods use the same 267 observations. Their thresholds were fixed using held-out groups from Coldcard with a 5% false-alert target. The observed rate for the candidate was 6 of 145 witnesses (4.1%). The 14-variable regression reached the same counts.

Across the nine external transfers, the two-variable model retrieves more sources at the same or lower false-alert count in four comparisons with inactivity alone. The inactivity rule remains the reference ranking method, with mean AP 0.792 versus 0.664 for the candidate. The candidate meets the 5% alert target on three of the nine external transfers. In the pooled Coldcard + CryptoBilis → BTCPay test, it retrieves 1 of 16 sources and flags 2 of 22 witnesses. Eight Coldcard histories are still unavailable for the detailed overlap audit.

## Selection history

| Date | Candidate | Reason |
| --- | --- | --- |
| 2026-11-24 | [Inactivity + balance logistic regression](experiments/2026-11-24-logistic-false-alert-budget.md) | Initial candidate, chosen for the strongest chronological gain at a lower alert count on the same test population. The three-incident evidence is exploratory. |

[Experiment history and update criteria](README.md)
