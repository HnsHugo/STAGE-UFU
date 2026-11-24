# Activity-feature ablation

Both tree families were refitted on the original training partitions and scored on the same test populations across all 49 configurations. The decision threshold remained 0.50. The table reports mean F1 with equal weight across the nine single-target external transfers.

| Feature set | Main tree | Smaller tree |
| --- | ---: | ---: |
| All 14 predictors | 0.390 | 0.323 |
| Without time since last activity | 0.369 | 0.331 |
| Without the four activity timing variables | 0.338 | 0.346 |
| Without timing and the six transaction and output counts | 0.338 | 0.348 |

The main tree split first on inactivity in 33 of 42 fits. With inactivity removed, it split first on balance in 36 of 42 fits. On Coldcard → CryptoBilis, removing the timing variables increased the main tree's retrieved sources from 49 to 59 of 122 and increased false alerts from 2 to 11. The pooled Coldcard + CryptoBilis → BTCPay trees retrieved no sources at 0.50 across the variants.

The four timing variables cover the time since first and last activity, the span of activity and the number of active blocks. The broad removal also drops the counts of confirmed, receiving and spending transactions and the counts of received, spent and unspent outputs. The remaining predictors in that variant are received amount, spent amount, balance and median spending fee rate.

[All configurations, incidents and aggregate metrics](2026-11-24-activity-ablation.csv) · [Experiment history](../README.md)
