# Three-incident test matrix

49 configurations cover every nonempty training and test subset of Coldcard, CryptoBilis and BTCPay. The outcome is documented source-cohort membership. The study is retrospective.

[Complete aggregate matrix and baselines](matrix.csv)

## Available observations

| Incident | Sources | Same-incident witnesses | Complete vectors |
| --- | ---: | ---: | ---: |
| Coldcard | 500 | 971 | 1471 |
| CryptoBilis | 122 | 207 | 329 |
| BTCPay | 16 | 32 | 48 |

The audit verified 1,792 Coldcard and CryptoBilis prefixes. Detailed evidence for 8 additional Coldcard prefixes is unavailable in this run. Known identities, reference payments and previously audited components from those rows still enter the linkage graph.

## External tests

The table gives one row per test incident inside each external cell. Mixed external test sets also have an equal-weight incident average and a pooled observation-level result in the CSV.

| Training | Test set | Test incident | Evaluated | Sources | Excluded | Groups | Tree recall | Tree F1 | Tree AP | Tree AUC | Inactivity AP | Reference chronology |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Coldcard | CryptoBilis | CryptoBilis | 267 | 122 | 62 | 253 | 0.4016 | 0.5665 | 0.6632 | 0.6884 | 0.8540 | train references earlier |
| Coldcard | BTCPay | BTCPay | 38 | 16 | 10 | 38 | 0.0000 | 0.0000 | 0.4211 | 0.4773 | 0.5710 | train references earlier |
| Coldcard | CryptoBilis + BTCPay | CryptoBilis | 267 | 122 | 62 | 253 | 0.4016 | 0.5665 | 0.6632 | 0.6884 | 0.8540 | train references earlier |
| Coldcard | CryptoBilis + BTCPay | BTCPay | 38 | 16 | 10 | 38 | 0.0000 | 0.0000 | 0.4211 | 0.4773 | 0.5710 | train references earlier |
| CryptoBilis | Coldcard | Coldcard | 1079 | 499 | 392 | 907 | 1.0000 | 0.9198 | 0.9390 | 0.9721 | 0.9557 | train references later |
| CryptoBilis | BTCPay | BTCPay | 41 | 16 | 7 | 40 | 0.4375 | 0.4667 | 0.4383 | 0.5700 | 0.5593 | train references earlier |
| CryptoBilis | Coldcard + BTCPay | Coldcard | 1079 | 499 | 392 | 907 | 1.0000 | 0.9198 | 0.9390 | 0.9721 | 0.9557 | train references later |
| CryptoBilis | Coldcard + BTCPay | BTCPay | 41 | 16 | 7 | 40 | 0.4375 | 0.4667 | 0.4383 | 0.5700 | 0.5593 | train references earlier |
| BTCPay | Coldcard | Coldcard | 1103 | 500 | 368 | 909 | 0.0000 | 0.0000 | 0.4533 | 0.3657 | 0.9554 | train references later |
| BTCPay | CryptoBilis | CryptoBilis | 296 | 122 | 33 | 256 | 0.0492 | 0.0678 | 0.3973 | 0.3838 | 0.8540 | train references later |
| BTCPay | Coldcard + CryptoBilis | Coldcard | 1103 | 500 | 368 | 909 | 0.0000 | 0.0000 | 0.4533 | 0.3657 | 0.9554 | train references later |
| BTCPay | Coldcard + CryptoBilis | CryptoBilis | 296 | 122 | 33 | 256 | 0.0492 | 0.0678 | 0.3973 | 0.3838 | 0.8540 | train references later |
| Coldcard + CryptoBilis | BTCPay | BTCPay | 38 | 16 | 10 | 38 | 0.0000 | 0.0000 | 0.4288 | 0.5270 | 0.5710 | train references earlier |
| Coldcard + BTCPay | CryptoBilis | CryptoBilis | 267 | 122 | 62 | 253 | 0.4016 | 0.5665 | 0.7390 | 0.5987 | 0.8540 | train references straddle test |
| CryptoBilis + BTCPay | Coldcard | Coldcard | 1078 | 499 | 393 | 906 | 1.0000 | 0.9207 | 0.9390 | 0.9720 | 0.9557 | train references later |

## All configurations

Micro scores count each held-out observation once. Macro scores average incident-level metrics with equal incident weight. An undefined incident metric leaves the corresponding macro metric blank.

| Training | Test | Type | Observations | Tree F1 micro | Tree AP micro | Tree AP macro | Smaller tree AP micro |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Coldcard | Coldcard | internal | 1471 | 0.9890 | 0.9836 | 0.9836 | 0.9809 |
| Coldcard | CryptoBilis | external | 267 | 0.5665 | 0.6632 | 0.6632 | 0.6982 |
| Coldcard | BTCPay | external | 38 | 0.0000 | 0.4211 | 0.4211 | 0.3789 |
| Coldcard | Coldcard + CryptoBilis | mixed | 1738 | 0.9269 | 0.9105 | 0.8234 | 0.9225 |
| Coldcard | Coldcard + BTCPay | mixed | 1509 | 0.9725 | 0.9637 | 0.7023 | 0.9666 |
| Coldcard | CryptoBilis + BTCPay | external | 305 | 0.5158 | 0.6314 | 0.5421 | 0.6517 |
| Coldcard | Coldcard + CryptoBilis + BTCPay | mixed | 1776 | 0.9137 | 0.8967 | 0.6893 | 0.9112 |
| CryptoBilis | Coldcard | external | 1079 | 0.9198 | 0.9390 | 0.9390 | 0.5090 |
| CryptoBilis | CryptoBilis | internal | 329 | 0.9195 | 0.8819 | 0.8819 | 0.8803 |
| CryptoBilis | BTCPay | external | 41 | 0.4667 | 0.4383 | 0.4383 | 0.4314 |
| CryptoBilis | Coldcard + CryptoBilis | mixed | 1408 | 0.9198 | 0.9274 | 0.9105 | 0.5721 |
| CryptoBilis | Coldcard + BTCPay | external | 1120 | 0.9076 | 0.9276 | 0.6886 | 0.5054 |
| CryptoBilis | CryptoBilis + BTCPay | mixed | 370 | 0.8729 | 0.8380 | 0.6601 | 0.8293 |
| CryptoBilis | Coldcard + CryptoBilis + BTCPay | mixed | 1449 | 0.9099 | 0.9180 | 0.7531 | 0.5679 |
| BTCPay | Coldcard | external | 1103 | 0.0000 | 0.4533 | 0.4533 | 0.4533 |
| BTCPay | CryptoBilis | external | 296 | 0.0678 | 0.3973 | 0.3973 | 0.4024 |
| BTCPay | BTCPay | internal | 48 | 0.5000 | 0.3333 | 0.3333 | 0.4583 |
| BTCPay | Coldcard + CryptoBilis | external | 1399 | 0.0143 | 0.4406 | 0.4253 | 0.4404 |
| BTCPay | Coldcard + BTCPay | mixed | 1151 | 0.0441 | 0.4368 | 0.3933 | 0.4391 |
| BTCPay | CryptoBilis + BTCPay | mixed | 344 | 0.1826 | 0.3667 | 0.3653 | 0.3831 |
| BTCPay | Coldcard + CryptoBilis + BTCPay | mixed | 1447 | 0.0487 | 0.4281 | 0.3946 | 0.4303 |
| Coldcard + CryptoBilis | Coldcard | internal | 1471 | 0.9379 | 0.9668 | 0.9668 | 0.9490 |
| Coldcard + CryptoBilis | CryptoBilis | internal | 329 | 0.8634 | 0.9157 | 0.9157 | 0.9325 |
| Coldcard + CryptoBilis | BTCPay | external | 38 | 0.0000 | 0.4288 | 0.4288 | 0.4556 |
| Coldcard + CryptoBilis | Coldcard + CryptoBilis | internal | 1800 | 0.9247 | 0.9556 | 0.9413 | 0.9444 |
| Coldcard + CryptoBilis | Coldcard + BTCPay | mixed | 1509 | 0.9231 | 0.9532 | 0.6978 | 0.9371 |
| Coldcard + CryptoBilis | CryptoBilis + BTCPay | mixed | 367 | 0.8033 | 0.8663 | 0.6723 | 0.8886 |
| Coldcard + CryptoBilis | Coldcard + CryptoBilis + BTCPay | mixed | 1838 | 0.9127 | 0.9448 | 0.7705 | 0.9348 |
| Coldcard + BTCPay | Coldcard | internal | 1471 | 0.9900 | 0.9865 | 0.9865 | 0.9790 |
| Coldcard + BTCPay | CryptoBilis | external | 267 | 0.5665 | 0.7390 | 0.7390 | 0.8618 |
| Coldcard + BTCPay | BTCPay | internal | 48 | 0.0000 | 0.4584 | 0.4584 | 0.4088 |
| Coldcard + BTCPay | Coldcard + CryptoBilis | mixed | 1738 | 0.9277 | 0.9347 | 0.8628 | 0.9630 |
| Coldcard + BTCPay | Coldcard + BTCPay | internal | 1519 | 0.9735 | 0.9805 | 0.7224 | 0.9663 |
| Coldcard + BTCPay | CryptoBilis + BTCPay | mixed | 315 | 0.5158 | 0.7205 | 0.5987 | 0.8254 |
| Coldcard + BTCPay | Coldcard + CryptoBilis + BTCPay | mixed | 1786 | 0.9144 | 0.9307 | 0.7280 | 0.9525 |
| CryptoBilis + BTCPay | Coldcard | external | 1078 | 0.9207 | 0.9390 | 0.9390 | 0.9258 |
| CryptoBilis + BTCPay | CryptoBilis | internal | 329 | 0.9020 | 0.9459 | 0.9459 | 0.9069 |
| CryptoBilis + BTCPay | BTCPay | internal | 48 | 0.2857 | 0.4076 | 0.4076 | 0.3617 |
| CryptoBilis + BTCPay | Coldcard + CryptoBilis | mixed | 1407 | 0.9171 | 0.9389 | 0.9424 | 0.9217 |
| CryptoBilis + BTCPay | Coldcard + BTCPay | mixed | 1126 | 0.9047 | 0.9317 | 0.6733 | 0.9179 |
| CryptoBilis + BTCPay | CryptoBilis + BTCPay | internal | 377 | 0.8410 | 0.9038 | 0.6767 | 0.8610 |
| CryptoBilis + BTCPay | Coldcard + CryptoBilis + BTCPay | mixed | 1455 | 0.9042 | 0.9318 | 0.7642 | 0.9136 |
| Coldcard + CryptoBilis + BTCPay | Coldcard | internal | 1471 | 0.9361 | 0.9697 | 0.9697 | 0.9449 |
| Coldcard + CryptoBilis + BTCPay | CryptoBilis | internal | 329 | 0.8421 | 0.8952 | 0.8952 | 0.9285 |
| Coldcard + CryptoBilis + BTCPay | BTCPay | internal | 48 | 0.2500 | 0.3785 | 0.3785 | 0.3823 |
| Coldcard + CryptoBilis + BTCPay | Coldcard + CryptoBilis | internal | 1800 | 0.9195 | 0.9544 | 0.9324 | 0.9404 |
| Coldcard + CryptoBilis + BTCPay | Coldcard + BTCPay | internal | 1519 | 0.9210 | 0.9547 | 0.6741 | 0.9307 |
| Coldcard + CryptoBilis + BTCPay | CryptoBilis + BTCPay | internal | 377 | 0.7857 | 0.8380 | 0.6368 | 0.8715 |
| Coldcard + CryptoBilis + BTCPay | Coldcard + CryptoBilis + BTCPay | internal | 1848 | 0.9073 | 0.9423 | 0.7478 | 0.9289 |

## Interpretation and verification

- Fourteen predictors use confirmed activity strictly before each reference block. Medians and missing-value indicators were calculated from each training partition. The fixed decision threshold is 0.50. The primary tree uses Gini, class weights, depth 3 and minimum leaf size 20. A prespecified depth-2 tree with a minimum leaf size of 5 provides a sensitivity check for small cohorts. Constant score, prior inactivity and prior balance provide ranking baselines.
- The overlap graph uses known addresses, references, pre-reference transactions, spent outputs, prior development components, exact vectors and observable funding and co-input links. Externally evaluated rows sharing a component with any training-incident identity are excluded. Internal test rows receive out-of-fold predictions from five globally grouped folds. Mixed cells combine out-of-fold predictions with the external predictions from the full training subset.
- Block chronology describes reference heights. Historical availability of the labels has not been established. The BTCPay pilot and any low-support or partial-audit cell carry explicit qualifications in the CSV. The cohort labels do not establish individual compromise or signing hardware.
- Ranking metrics were independently recomputed from the saved predictions. The frozen pooled models replayed 1,800 previous out-of-fold predictions and 190 private BTCPay predictions. The frozen internal and bidirectional evaluations also passed their replay verifiers.

## Related results

- [Grouped within-incident tests](../../within_incident_20261119/RESULTS.md)
- [Coldcard and CryptoBilis transfers](../../bidirectional_transfer_20261119/RESULTS.md)
- [Pooled Coldcard and CryptoBilis tests](../../pooled_incidents_20261119/RESULTS.md)
- [BTCPay pilot protocol](../../btcpay_test_preparation_20261120/README.md)
