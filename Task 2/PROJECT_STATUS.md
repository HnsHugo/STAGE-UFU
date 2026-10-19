# Project status — 19 October 2026

## Current priority

The main path is the Coldcard coursework, address tracing and carefully sourced hardware-wallet-related case studies. Hugo's meeting notes mention another case related to Ledger and combining it with Coldcard. Its exact reference, address roles and the professor's code have not yet been supplied in this repository. Those details remain pending.

## Completed work

- [Equal-duration collection comparison](research/external_cases/TEMPORAL_COLLECTION_COMPARISON.md): Coldcard, two provisional CryptoBilis recipients and one documented EFF recipient in 24-hour windows. One-output/same-block properties also occur in an EFF observation; no standalone discriminator or accuracy claim follows. Historical models remain unchanged.
- [Collection-pattern pilot](research/external_cases/COLLECTION_PATTERNS.md): focused hardware-related source screening, two provisional recipients, 129 confirmed transactions collected and 122 receipts retained before the historical cutoff. Source assertions and hardware control remain distinct; no classifier is trained.
- The course exercise: ten transaction features, 100 payments to the course address and 100 same-block unattributed comparisons, a decision tree and saved results.
- Observed case flows, parent coverage, timestamps, fees and dated spending observations for five source-attributed consolidations.
- Integrity checks for 493,571 unique transactions in 98 selected blocks, with 1,070 recovered candidate parents out of 2,349 requested.
- Exploratory random/chronological comparisons, group-held-out evaluation and fixed univariate baselines. Results and failures are retained.
- Offline Elliptic++ and Real-CATS source-label benchmarks, external descriptive scoring, schema checks and an overlap audit.
- Real-CATS validation-error, missingness-only, family-permutation, ablation and three-seed stability diagnostics. They are supplementary development experiments, not independent theft detection.
- A reproducible demo and automated tests.

## Results that need context

| Result | Meaning and limit |
| --- | --- |
| Classroom tree: 60/60 on its sample test | A small test linked to the same address and case; not a general hardware-wallet detector |
| Grouped tree: 874/1,070 candidates recovered | Internal case-relation labels; one candidate group is entirely missed |
| Grouped tree: 1,072 background alerts | Unattributed transactions are not certified legitimate, so these are not confirmed false positives |
| Real-CATS full forest: mean validation AP 24.42% over three seeds | Fixed-split source-category development benchmark |
| Without monetary family: mean validation AP 25.21% | AP difference changes sign by seed; F1 is lower on all three seeds; no replacement model selected |
| FSF external score approximately 0.021, below 0.15 | Descriptive score of the frozen source-category model, not a calibrated theft probability |

FSF shares two multi-recipient transactions with training addresses. This is observed data overlap, not common-ownership proof. The historical reports retain their collection dates and original limitations.

## Partial or blocked

- Hot/cold training for September 2026: six research windows have count-consistent coverage, but no address has verified label validity for the full window. No training is authorized by those old labels.
- Hardware-wallet identification: no validated address-to-device ground truth has been established.
- Cross-case/incident generalization: independent roles, entity groups and time-valid labels remain insufficient.
- GNN/GCN or other graph models: no completed Task 2 experiment. The article outline proposes exploration, not a settled architecture.
- Ledger extension and reproduction of Ivan's experiment: await the exact case reference and code.

## What changed in this reorganization

Parts 1–5 now form the main reading path. Scripts and historical results have been moved into research and supplementary folders. User-facing documentation and generated flow reports use English. Saved numerical artifacts, model parameters and raw evidence bytes have been preserved. See [Migration](docs/MIGRATION.md) and [Verification](verification/README.md).

## Next action

Expand documented comparison entities and collection contexts beyond one low-activity donation address; prespecify calendar/volume/maturity controls before evaluating discrimination. Keep the provisional CryptoBilis case separate; the professor's exact reference and code remain pending. Preserve case IDs so that mixing datasets does not silently mix related transactions between training and evaluation.
