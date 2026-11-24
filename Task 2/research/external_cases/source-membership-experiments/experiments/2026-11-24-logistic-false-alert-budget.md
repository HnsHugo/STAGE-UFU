# Logistic regression at a training false-alert budget

On the nine frozen single-target external transfers, compare inactivity and balance scores, the two saved tree families and fixed logistic models. The logistic variants use balance alone, inactivity plus balance, all 14 predictors and the three previously defined feature removals. Logistic regression uses L2 regularization (C = 1), balanced class weights and standardized signed log-transformed numeric features. Median imputation and scaling use each training partition. Missingness indicators are preserved for the features used.

Cutoffs target a maximum 5% false-alert rate on the grouped out-of-fold scores of the training subset. Tied witness scores are kept together. Apply each fixed cutoff to the external population scored by the full training fit, and report the observed false-alert rate.

## Coldcard to CryptoBilis

| Method | Sources retrieved / 122 | False alerts / 145 | AP |
| --- | ---: | ---: | ---: |
| Inactivity | 60 | 7 | 0.8540 |
| Balance | 25 | 10 | 0.7657 |
| Inactivity + balance logistic regression | 100 | 6 | 0.9608 |
| All 14 predictors logistic regression | 100 | 6 | 0.9554 |

Across the nine transfers, the two-variable regression recovered more sources with equal or fewer false alerts than inactivity alone in four cases. Its average AP was 0.664, versus 0.792 for inactivity; this is an equal-weight average across the transfer comparisons. Its realized false-alert rate met the 5% target in three cases. The logistic feature removals showed no consistent improvement.

In Coldcard + CryptoBilis → BTCPay, the two-variable regression retrieves one of 16 sources and signals two of 22 witnesses. The inactivity rule retrieves four sources and signals five witnesses. These external results include retrospective directions and a partial detailed Coldcard overlap audit.

[All nine transfers, thresholds and confusion counts](2026-11-24-logistic-false-alert-budget.csv) · [Current candidate](../CURRENT.md) · [Experiment history](../README.md)
