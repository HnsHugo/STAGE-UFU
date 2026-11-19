# Bidirectional Coldcard and CryptoBilis transfer

Two shallow trees were fitted on 19 November 2026. Each uses all available complete vectors from one incident and scores only complete addresses in the other incident that pass the measured-overlap audit. The unit is a source address with a fixed reference payment. The label is membership in each incident's documented source cohort.

## Held-out incident results

| Train → test | Train n | Test n | Precision | Recall | F1 | Average precision | ROC AUC | TP | FP | FN | TN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Coldcard → CryptoBilis | 1,471 | 271 | 0.9608 | 0.4016 | 0.5665 | 0.6591 | 0.6867 | 49 | 2 | 73 | 147 |
| CryptoBilis → Coldcard | 329 | 1,081 | 0.8515 | 1.0000 | 0.9198 | 0.9390 | 0.9722 | 499 | 87 | 0 | 495 |

| Average precision on the same test rows | Coldcard → CryptoBilis | CryptoBilis → Coldcard |
| --- | ---: | ---: |
| Shallow tree | 0.6591 | 0.9390 |
| Prior inactivity | **0.8540** | **0.9557** |
| Prior balance | 0.7636 | 0.8240 |
| Constant score | 0.4502 | 0.4616 |

The Coldcard-trained tree finds 49 of 122 eligible CryptoBilis sources. The reverse tree finds all 499 eligible Coldcard sources and flags 87 of the 582 comparisons. Prior inactivity yields higher average precision in both directions.

## Population and fitting protocol

| Test incident | Selected | Complete vectors | Held out for overlap | Incomplete prefixes | Scored |
| --- | ---: | ---: | ---: | ---: | ---: |
| CryptoBilis | 366 | 329 | 58 | 37 | 271 (122 cases / 149 comparisons) |
| Coldcard | 1,500 | 1,471 | 390 | 29 | 1,081 (499 cases / 582 comparisons) |

The training populations are 500 Coldcard cases and 971 comparisons, and 122 CryptoBilis cases and 207 comparisons. The fourteen allowlisted predictors use only confirmed activity strictly below each address's reference block. The code fits medians on the training incident alone and appends one missingness indicator per predictor. Both trees use Gini, depth at most three, minimum leaf size 20, balanced class weights, seed 42 and a threshold of 0.5. Both fits use the fixed settings. Test scores were used only for evaluation.

All 1,866 selected identities enter the overlap check. Address hashes, prior/reference transaction hashes and exact complete predictor vectors define measured links. An incomplete row contributes only its known address and reference links. The new audit reproduces the 1,281 historical components on the earlier snapshot and independently reconstructs 1,217 components on the new one. Four components span both incidents. The test members of all four are excluded in each direction. This controls observed links, with residual uncertainty about entity ownership and incomplete paths.

This is a retrospective study of two previously inspected incidents. CryptoBilis → Coldcard is reverse time. The scores measure source-cohort membership, with compromise, signing device and seed origin remaining unverified labels. Both experiments use different target populations, so the directional F1 gap is descriptive. Keep a separately identified third incident outside training and model choice until the pooled evaluation is defined.

## Reproduction and audit

- [Protocol and input pins](protocol.json) and [pre-fit evidence audit](preflight.json)
- [Eligibility manifest](eligibility.json.gz), [model exports](models.json) and [per-address predictions](predictions.json.gz)
- [Results CSV](metrics.csv) and [full metrics and supports](summary.json)

The pre-fit checks recounted all 1,800 complete vectors, including 93 newly available Coldcard vectors. Eight of these were reconstructed from the pinned pre-existing private archives. The verifier replays the complete test predictions from the exported trees in float32, checks training-only imputation and weighted node support, and independently recomputes the scores and counts. It verifies 1,352 predictions and eight ranking metric sets without fitting. Thirty existing scientific guard tests also passed. This unit used no blockchain API and changed no prior cohort or model.

To replay the public results from the repository root:

```sh
python3 "Task 2/research/external_cases/bidirectional_transfer_20261119/run_transfer.py" verify
```

To regenerate in a separate result directory, point `--raw-archives` to the private directory that contains one subdirectory per archived scope. The eight archive filenames and fingerprints are pinned through each scope's backup manifest. Use the NumPy and scikit-learn versions in the protocol.

```sh
runner="Task 2/research/external_cases/bidirectional_transfer_20261119/run_transfer.py"
python3 "$runner" prepare --raw-archives /path/to/archives --output /path/to/new-results
python3 "$runner" fit --output /path/to/new-results
python3 "$runner" verify --output /path/to/new-results
```
