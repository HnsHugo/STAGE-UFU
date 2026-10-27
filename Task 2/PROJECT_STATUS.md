# Project status — 27 October 2026

## Current priority

The original Teams instructions, meeting notes and Overleaf files now establish
the missing second stage: **the dataset and classifier of robbed source
addresses**, expected to relate to hardware wallets. Read the reconciled
[alignment reference](ALIGNMENT.md). The [Coldcard source registry](research/coldcard/source_registry_20261027/README.md)
has now been executed: 500 candidate-day addresses / 1,324 inputs, with five later
addresses kept separate. Next is a small deterministic pre-payment history/feature
pilot. Collector rankings remain supporting results, not this target. No model
was fitted in the registry unit; all compromise/device labels remain unknown.

## Completed work

- [Coldcard source-address evidence registry](research/coldcard/source_registry_20261027/README.md):
  pinned complete history reused; 505 address records and 1,331 exact input/outpoint
  evidence records generated locally, with a committed reproducible protocol and
  aggregate summary. Candidate-day and later receipts remain separate; role,
  confidence, collection/review dates and unknown compromise/hardware labels are
  explicit. Nine focused tests and the execution log document verification.
- [Central complete-block ranking](CENTRAL_EXPERIMENT.md): 30,938 transactions, two incident groups, full recipient populations and three label-blind baselines. Anonymous offline rank evidence, prefix ranks, cross-provider receipt agreement and tie-aware reference coverage are saved; complete address cohorts remain local.
- [Expanded collection comparison](research/external_cases/EXPANDED_COLLECTION_COMPARISON.md): the original FSF history was recovered with its expected hash. Nine 24-hour windows now cover two incident groups and two comparison organizations. FSF's retrospective stress day has 25 receipts, but dates/fees are not matched to the incidents; no model fitting or accuracy claim follows.
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

- Robbed source-address dataset/model: graph-evidence registry completed, but
  per-address compromise/device labels, complete source histories and documented
  controls are missing. The requested supervised classifier is not completed.
- Network-relative fees, CPFP and RBF: the Teams request for a focused literature
  review of preprocessing is explicit; completion of that synthesis and a
  justified experiment is not evidenced by the reviewed main-path material.
- Source-side topology/H1 and the finished paper/presentation remain to develop;
  graph heuristics must not be treated as proven ownership.
- Hot/cold training for September 2026: six research windows have count-consistent coverage, but no address has verified label validity for the full window. No training is authorized by those old labels.
- Hardware-wallet identification: no validated address-to-device ground truth has been established.
- Cross-case/incident generalization: independent roles, entity groups and time-valid labels remain insufficient.
- GNN/GCN or other graph models: no completed Task 2 experiment. Teams requests
  evaluation; the article introduction proposes a GNN while the main outline
  leaves its suitability open. Related work and dataset design must justify it.
- Ledger extension: CryptoBilis case selection is established; exact participant identifiers, hardware-control labels and reproduction of Ivan's code remain pending.

## What changed in this reorganization

Parts 1–5 now form the main reading path. Scripts and historical results have been moved into research and supplementary folders. User-facing documentation and generated flow reports use English. Saved numerical artifacts, model parameters and raw evidence bytes have been preserved. See [Migration](docs/MIGRATION.md) and [Verification](verification/README.md).

## Next action

Build a small deterministic pilot of source-address histories/features, with each
observation cut off before its source's payment. Start with the completed
[registry](research/coldcard/source_registry_20261027/README.md), document coverage
and distinguish graph-candidate features from verified compromise/hardware
labels. Do not restart the completed registry or another recipient ranking.
