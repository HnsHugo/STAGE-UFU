# Project status — 30 October 2026

## Current priority

**Latest resumption update:** Hugo requested continued spaced retries. After
same-route source-counter HTTP 200, the distinct
[653-source retry](research/coldcard/comparison_retry_20261030_1841/README.md)
attempted 274 addresses: **233 complete, 39 incomplete, two HTTP 429 errors and
379 pending**. All 272 raw responses re-extract. The first-denial guard stopped
scheduling at 19:07 UTC; the collector is no longer active. The immutable 80/200
milestones and every earlier pass remain intact. The latest combined 1,500-row
view has **500 complete cases, 506 complete comparisons, 113 incomplete
comparisons, 101 latest known errors and 280 never attempted**. Thus 1,006
rows have the fourteen predictors; 381 comparison network gaps remain.
[Hourly retry control](research/coldcard/comparison_access_retries_20261030/README.md)
is confirmed enabled. The published lease is cleared. No request is eligible
before 21:07:49 UTC (two hours after the last 429); subsequent 429s increase
backoff and a longer Retry-After prevails. No collector/model/split is active.
All 86 source-path tests pass. Earlier blocked counts below are historical.

The original Teams instructions, meeting notes and Overleaf files now establish
the missing second stage: **the dataset and classifier of robbed source
addresses**, expected to relate to hardware wallets. Read the reconciled
[alignment reference](ALIGNMENT.md). The [Coldcard source registry](research/coldcard/source_registry_20261027/README.md)
has now been executed: 500 candidate-day addresses / 1,324 inputs, with five later
addresses kept separate. The [pre-payment pilot](research/coldcard/prepayment_pilot_20261027/README.md)
has now collected eight complete source histories and computed fourteen strictly
prior-block features for each. All eight have one earlier receipt and no earlier
spending; nine columns are constant and the spending-fee column is missing.
The [multi-input extension](research/coldcard/multiinput_pilot_20261028/README.md)
adds four complete histories and the same fourteen features. They have two or
three prior receipts and no prior spending. Those two pilots provided twelve distinct source
histories; all remain in one incident group with unknown compromise/device labels.
The [resumable cohort pipeline](research/coldcard/source_cohort_20261028/README.md)
has reused the twelve histories and finished all 25 fixed batches.
The final run executed batches 22–25: **68 fixed attempts**,
**66 complete histories**, 0 errors and 2 incomplete histories.
Original protocol coverage is **473/500 complete, 24 retained errors, 3 incomplete and
0 pending**, with 17 sources showing prior spending.
All 432 earlier entries were unchanged; the original protocol is exhausted.
The separate [supplemental recovery](research/coldcard/source_cohort_recovery_20261029/README.md)
has now attempted the 27 gaps under explicit 16-page/15-second bounds: 27
complete, 0 errors and 0 incomplete histories. Combined feature coverage is
**500 complete, 0 errors, 0 incomplete and 0 pending**; original outputs and all 473 complete entries are preserved.
The [focused label review](research/coldcard/source_label_review_20261029.json)
and per-source eligibility still have zero verified compromise/device labels,
zero documented negative controls and one incident group. A
[five-source exact-identifier pilot](research/coldcard/source_label_adjudication_20261030/README.md)
has now executed ten fixed address/TXID searches. It found explorer observations,
but no qualifying individual compromise/device assertion in that bounded review;
all labels remain unknown. The other 495 sources were not individually searched.
A subsequent [external reconstruction comparison](research/coldcard/source_corroboration_20261030/README.md)
now corroborates all **500 source addresses and 500 reference payments** against
two public reconstructions. Address/value/count and 1,324 input-value observations
agree with SomaxBT; payment anchors, counts, amounts and fees agree with Alvaro P.
The new case-relation layer is `source_attributed`; individually verified
compromise/device labels remain unknown. Original predictors and reports are
unchanged. The [first-person report review](research/coldcard/owner_report_adjudication_20261030/README.md)
now maps one public author's loss/device account exactly to `cohort_0002`, its
reference payment and five spent UTXOs. A separate evidence tier records one
owner-reported loss and Coldcard association; no independent identity/control,
firmware or signing-device proof was established. The other 499 records and
original labels are unchanged. The 30 October alignment review corrects the
priority: the existing 500-source feature/evidence view and source description
are now [consolidated](research/coldcard/source_dataset_20261030/README.md).
The [comparison protocol](research/coldcard/source_comparison_design_20261030/README.md)
now states a narrow exploratory core-membership target and evaluation. Its
[same-block selector](research/coldcard/source_comparison_selection_20261030/README.md)
has retained 1,000 fixed comparisons from 5,025 eligible sources. Their
[initial history collection](research/coldcard/comparison_histories_20261030/README.md)
is preserved at 40 complete, twelve incomplete, 668 errors and 280 pending.
Original-route HTTP 200 allowed a distinct
[948-source recovery](research/coldcard/comparison_network_recovery_20261030/README.md):
297 attempts yielded 233 complete, 62 incomplete and two HTTP 429 errors, leaving
651 pending. A [653-source cooldown continuation](research/coldcard/comparison_rate_limit_continuation_20261030/README.md)
waited over fifteen minutes, reduced the global rate to one request/second and
stopped after two further HTTP 429 results. No other source started. The latest
combined view retains 500 complete cases plus 1,000 selected comparisons:
273 complete, 74 incomplete, 373 latest known errors and 280 never attempted.
The stopped continuation has 651 pending IDs; 371 retain old errors and 280 are
never attempted. All original outcomes and 295 recovery raw responses are audited;
85 source-path regressions pass. The current blocker is persistent HTTP 429,
not the earlier tunnel 403. No collector is active.
Further public reports
are bounded enrichment; obtaining individual testimony for every address was not
a documented professor requirement.
Collector rankings remain supporting results. No model was fitted.

## Completed work

- [Preserved recovery and cooldown continuation](research/coldcard/comparison_rate_limit_continuation_20261030/README.md):
  233 new complete and 62 incomplete histories retained; all 295 raw responses
  re-extract. The immediate stop guard limited the first HTTP 429 interruption to
  two started attempts. One distinct slower continuation after fifteen minutes
  also received two 429s, with no further source scheduled. Both pass checkpoints,
  all initial results and the 500 case vectors are preserved. A reproducible
  1,500-row view retains all three pass outcomes and the 14-feature allowlist;
  773 rows have complete predictors. No model or split. All 85 source-path tests pass.
- [Comparison collection and blocked-network recovery](research/coldcard/comparison_histories_20261030/README.md):
  36 fixed batches / 720 attempts, 40 complete, twelve incomplete, 668 errors and
  280 pending. All 52 raw histories were re-extracted and fifteen finished attempt
  markers recovered without HTTP. The 500 case vectors are unchanged. A defect
  in recognizing URLError tunnel 403 refusals allowed excess failed attempts;
  corrected denied-batch/resume checks and 73 passing source-path tests are saved.
  Collection is incomplete, network blocked, and all complete comparisons fall
  in the first reference block. No split or model.
- [Comparison design and actual source selection](research/coldcard/source_comparison_selection_20261030/README.md):
  target, same-period input-source universe, quotas, failures and exploratory
  grouped evaluation are frozen. Four complete new provider snapshots reconcile
  all 500 case sources; 5,526 unique source addresses before exclusions, 5,025
  eligible comparisons and 1,000 selected with zero quota shortfall. Raw-cache
  reproduction and public redacted-census replay agree exactly. Eleven focused
  tests bring the source-path total to 60. No comparison histories, split or model.
- [Consolidated source dataset and descriptive analysis](research/coldcard/source_dataset_20261030/README.md):
  500 rows with fourteen unchanged prior-block predictors, separate case/owner
  evidence, source provenance and an explicit predictor allowlist. 411 sources
  have exactly one prior transaction and 482 no prior spending. Reference payments
  consume all known prior-block UTXOs for 499 sources; `cohort_0435` consumes
  200 of 225, leaving 25 known outputs outside that payment. Seven new focused
  tests and 49 passing source-path tests; exact offline reproduction and independent
  feature/cutoff/outpoint accounting checks. No new collection or fitting.
- [First-person owner-report adjudication](research/coldcard/owner_report_adjudication_20261030/README.md):
  one account maps exactly to `cohort_0002`; the original post, payment comment
  and follow-up timeline are one report. Five input outpoints match the known
  prior-block holdings. Reported loss/Coldcard association is kept separate from
  verified compromise, seed origin and signing-device labels. Eight new tests
  and 42 passing source-path regressions protect roles, deduplication and unknowns.
- [External case-source corroboration](research/coldcard/source_corroboration_20261030/README.md):
  500/500 exact source/payment comparisons agree with both pinned reconstructions;
  1,324 input-value observations reconcile. Hashes, byte-preserved snapshots,
  per-source comparisons, evidential limits and seven new regression tests are
  recorded. Exact external prevout IDs are unavailable; no device/victim label
  was promoted and no model changed.
- [30 October validation](verification/source_cohort_validation_20261030.json):
  500 complete histories, 27 raw recoveries re-extracted, 473 inherited entries
  unchanged, exact offline restoration and 18 passing regressions. The recovery
  was published as commit `b755a9829bdf7a449935045e267c7612d4203822`.
- [Five-source label adjudication](research/coldcard/source_label_adjudication_20261030/README.md):
  ten prespecified exact-identifier searches; explorer matches for all five,
  zero qualifying individual labels and no label promotion. Query/retrieval
  hashes, source-specific decisions, scope limits and missing proof are saved.
- [Supplemental recovery and label eligibility](research/coldcard/source_cohort_recovery_20261029/README.md):
  one fixed 27-source pass, 27 recovered complete histories, 0 errors,
  0 incomplete, combined 500/500 complete. All 473 earlier complete records
  and original errors are preserved. Both exports and per-source eligibility
  reproduce offline; 27 new raw histories were re-extracted and exact
  no-network restoration passed. The evidence review distinguishes graph
  relation, compromise, seed origin and signing device; training remains blocked
  by individual labels, controls and incident-level evaluation design.
- [Final source collection, batches 22–25](research/coldcard/source_cohort_20261028/README.md):
  68 fixed attempts (20/20/20/8), 66 new complete histories,
  0 errors and 2 incomplete histories. All 432 earlier records remain
  identical. Cumulative coverage: 473 complete, 24 errors, 3 incomplete,
  0 pending; 997 prior observations and 986 distinct transaction references.
  All four exports reproduce offline; 68 new raw histories were re-extracted,
  and the final checkpoint restores exactly without raw files or requests.
  Earlier raw histories were unavailable in this fresh checkout; their preserved
  normalized evidence and complete feature vectors were verified offline.
- [Automatic source collection, batches 20–21](research/coldcard/source_cohort_20261028/README.md):
  40 fixed attempts, 38 complete histories, 2 errors and 0 incomplete histories.
  All 392 earlier records are identical; completed snapshots were verified before
  continuation. Cumulative coverage: 407 complete, 24 errors, 1 incomplete,
  68 pending; 817 prior observations and 808 distinct transaction references.
  Raw re-extraction, offline reproduction/restore and source-selection checks passed.
- [Automatic source collection, batches 18–19](research/coldcard/source_cohort_20261028/README.md):
  40 fixed attempts, 34 complete histories, 6 errors and 0 incomplete histories.
  All 352 earlier records are identical; completed snapshots were verified before
  continuation. Cumulative coverage: 369 complete, 22 errors, 1 incomplete,
  108 pending; 757 prior observations and 749 distinct transaction references.
  Raw re-extraction, offline reproduction/restore and source-selection checks passed.
- [Automatic source collection, batch 17](research/coldcard/source_cohort_20261028/README.md):
  20 fixed attempts, 20 complete histories, 0 errors and 0 incomplete histories.
  All 332 earlier records are identical; completed snapshots were verified before
  continuation. Cumulative coverage: 335 complete, 16 errors, 1 incomplete,
  148 pending; 695 prior observations and 688 distinct transaction references.
  Raw re-extraction, offline reproduction/restore and source-selection checks passed.
- [Automatic source collection, batches 14–16](research/coldcard/source_cohort_20261028/README.md):
  60 fixed attempts, 58 complete histories, 2 errors and 0 incomplete histories.
  All 272 earlier records are identical; completed snapshots were verified before
  continuation. Cumulative coverage: 315 complete, 16 errors, 1 incomplete,
  168 pending; 619 prior observations and 613 distinct transaction references.
  Raw re-extraction, offline reproduction/restore and source-selection checks passed.
- [Automatic source collection, batches 12–13](research/coldcard/source_cohort_20261028/README.md):
  40 fixed attempts, 40 complete histories, 0 errors and 0 incomplete histories.
  All 232 earlier records are identical; completed snapshots were verified before
  continuation. Cumulative coverage: 257 complete, 14 errors, 1 incomplete,
  228 pending; 535 prior observations and 531 distinct transaction references.
  Raw re-extraction, offline reproduction/restore and source-selection checks passed.
- [Automatic source collection, batches 10–11](research/coldcard/source_cohort_20261028/README.md):
  40 fixed attempts, 39 complete histories, 0 errors and 1 incomplete history.
  All 192 earlier records are identical; completed snapshots were verified before
  continuation. Cumulative coverage: 217 complete, 14 errors, 1 incomplete,
  268 pending; 463 prior observations and 459 distinct transaction references.
  Raw re-extraction, offline reproduction/restore and source-selection checks passed.
- [Automatic source collection, batches 8–9](research/coldcard/source_cohort_20261028/README.md):
  40 fixed attempts, 32 complete histories, 8 errors and 0 incomplete histories.
  All 152 earlier records are identical; completed snapshots were verified before
  continuation. Cumulative coverage: 178 complete, 14 errors, 0 incomplete,
  308 pending; 401 prior observations and 397 distinct transaction references.
  Raw re-extraction, offline reproduction/restore and source-selection checks passed.
- [Automatic source collection, batches 6–7](research/coldcard/source_cohort_20261028/README.md):
  40 fixed attempts, 40 complete histories, 0 errors and 0 incomplete histories.
  All 112 earlier records are identical; completed snapshots were verified before
  continuation. Cumulative coverage: 146 complete, 6 errors, 0 incomplete,
  348 pending; 238 prior observations and 235 distinct transaction references.
  Raw re-extraction, offline reproduction/restore and source-selection checks passed.
- [Automatic source collection, batches 4–5](research/coldcard/source_cohort_20261028/README.md):
  40 fixed attempts, 40 complete histories, 0 errors, and all 72 earlier records
  unchanged. Each batch was exported and verified before the next started.
  Cumulative coverage: 106 complete, 6 errors, 0 incomplete and 388 pending;
  179 prior observations and 177 distinct transaction references. Raw
  re-extraction, offline reproduction/restore and source-selection checks passed.
- Automatic continuation: `source_cohort.py run-many` chains the original fixed
  batches, exports/verifies each result, recovers a missing export and checks a
  soft budget between batches. Two workers, terminal failures and frozen features
  are unchanged. Six new regression tests cover the orchestration.
- [Source cohort batch 3](research/coldcard/source_cohort_20261028/README.md):
  twenty fixed attempts, 16 new complete histories and all 52 earlier records unchanged.
  Cumulative coverage is 66 complete, 6 errors, 0 incomplete and 428 pending;
  100 prior observations, 99 distinct transaction references and 2 prior-spending sources.
  Seven regression tests, raw re-extraction and offline restore/reproduction
  checks passed. No new labels, independent incident groups or fitted models.
- [Source cohort batch 2](research/coldcard/source_cohort_20261028/README.md):
  twenty fixed attempts, 20 new complete histories and no prior-record changes.
  Cumulative coverage is 50 complete, 2 errors, 0 incomplete and 448 pending;
  63 prior observations, 63 distinct transaction references and 2 prior-spending sources.
  Seven regression tests, raw re-extraction and offline restore/reproduction
  checks passed. One incident, unknown labels and no classifier fitting remain.
- [Resumable source cohort, historical batch 1](research/coldcard/source_cohort_20261028/README.md):
  fixed 500-source plan, twelve cached histories reused, twenty new attempts,
  thirty complete vectors overall and two retained timeouts. Atomic checkpoints,
  unfinished-batch recovery, raw-orphan recovery, offline restoration and
  immutable snapshots are implemented and tested. Forty-one prior transaction
  observations and one prior-spending source are available; unknown labels and
  the single incident group remain unchanged.
- [Multi-input source pilot](research/coldcard/multiinput_pilot_20261028/README.md):
  four deterministically selected sources among 81 eligible candidates, complete
  bounded collection and an unchanged feature extractor. Nine prior transaction
  IDs are distinct and do not overlap the first pilot. Four small received
  outputs (294, 294, 294 and 330 satoshis) were retained. Labels remain unknown;
  neither 4/4 data coverage nor the twelve-source combined set is model accuracy.
- [Pre-payment source feature pilot](research/coldcard/prepayment_pilot_20261027/README.md):
  eight fixed SHA256-selected sources, eight complete two-transaction histories,
  prior-block UTXO reconstruction and fourteen feature definitions. Published
  prefix-only evidence reproduces the feature rows offline; raw snapshots have
  pinned hashes. Future/same-block activity and current spent flags are excluded.
  This small sample contains only single-input reference payments and is not
  representative of the 81 multi-input sources or an independent test set.
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

- Robbed source-address dataset/model: original collection ended at 473 complete,
  24 errors and 3 incomplete; separate supplemental recovery now yields
  500 complete, 0 errors, 0 incomplete and 0 pending. Independently verified per-address compromise/device labels and documented
  controls remain absent; the new separate owner-report tier has one sourced account. The supervised classifier is not completed.
  Historical spending-fee features cannot be inferred from the
  reference payment when no prior source spending exists.
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

The stopped retry retains 381 network gaps: two latest 429 errors and 379 pending
IDs (99 retaining prior errors and 280 never attempted). The confirmed hourly task
will skip requests until the saved two-hour delay or any longer Retry-After has
elapsed, then make one normal source-counter check on the original route. After
200, create a distinct pinned successor pass; never silently restart the denied
pass. Scheduled iterations collect at most five fixed batches, verify/export
before continuing, preserve all earlier results and publish the actual outcomes.
An active lease/OS lock skips a concurrent run; a new 403 pauses the task without
route/provider changes. Pause automation once no network gaps remain.
The 113 bounded-incomplete histories require a separate coverage decision.
No complete comparisons exist in block 960191; audit class/block attrition and
connected-component group gates before any exploratory fit. Operational membership
zero and unknown compromise/device labels remain distinct. No model is fitted.
