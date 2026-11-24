# Inactivity thresholds chosen by training F1

For each training subset, select the inactivity threshold with the highest training F1. Ties use the higher threshold. Missing inactivity uses the training median. Compare on the nine single-target external populations from the three-incident matrix, with the two trees held at their original 0.50 cutoffs.

The rule had a higher F1 than both trees in seven transfers and tied the better tree in two. The learned thresholds ranged from 67 to 6,849 blocks. For Coldcard → CryptoBilis, the rule found 81 of 122 sources and flagged 7 of 145 witnesses. The original main tree found 49 sources and flagged 2 witnesses. For pooled Coldcard + CryptoBilis → BTCPay, the rule found 7 of 16 sources and flagged 6 of 22 witnesses. The original main tree found zero sources and flagged one witness.

[All nine transfers and confusion counts](2026-11-24-inactivity-threshold.csv) · [Experiment history](../README.md)
