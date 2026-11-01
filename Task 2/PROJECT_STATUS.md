# Project status — 30 October 2026

**Verified pre-cutoff continuation — 1 November 2026 UTC:** The distinct 99-source successor reused 24 fingerprint- and cursor-verified HTTP-200 responses offline, finalized 80 sources, then stopped on the first new HTTP429 without retry. Results: four complete prior prefixes, 76 bounded-incomplete and 19 network gaps. All 80 raw tails re-extract, all four new vectors were independently recounted, and 1,422 saved response fingerprints verify. The schema-v2 view now preserves 500 case and 876 comparison predictor vectors (1,376 total); full-current-history comparison statuses remain separately 864 complete and 136 incomplete. The 105 bounded-incomplete prefix results supply no vector. Labels, strict cutoffs and fourteen definitions are unchanged. The lease is idle; no provider request is allowed before 2026-11-01T23:20:04.694868+00:00. Resume only a separately pinned successor over the 19 IDs in the latest checkpoint; never rerun the denied pass.

Latest artifacts: `research/coldcard/reference_tail_continuation_20261101_0653/`; exact resumption: `resume_checkpoint.json` in that folder. Older progress entries below are historical.

**Validated pre-cutoff recovery — 31 October 2026 UTC:** The anchored pre-cutoff method matched every prior transaction and all fourteen predictors for eight full-history controls across all four blocks. Application to 136 unfinished comparisons then saved 37 results: eight complete prior prefixes and 29 bounded-incomplete; HTTP429 stopped two already-started requests, leaving 99 sources without a final prefix result. All eight new vectors were independently recounted, all 37 raw tails re-extract and 621 saved response fingerprints verify. The explicit pre-cutoff feature view has 500 complete case vectors and 872 comparison vectors, with 128 comparison vectors unavailable. Full-current-history comparison statuses remain 864 complete and 136 incomplete. Labels, cutoffs, all 1364 previous vectors and baseline bytes are preserved. A pre-cutoff cursor audit is separately labeled from full-current-history counter reconciliation. No model/split. The lease is idle and no provider request is allowed before 2026-11-01T06:25:21.786387+00:00. Two HTTP429 records and all successful pages are preserved. Resume only a separately pinned successor over the 99 network gaps; retain the 29 bounded-incomplete outcomes.

Latest artifacts: `research/coldcard/reference_tail_coverage_20261031_221432/`; exact resumption: `resume_checkpoint.json` in that folder. Older progress entries below are historical.


**Supplemental coverage — 31 October 2026 UTC:** Supplemental coverage recovered 24 complete comparison histories from the 160 previously bounded-incomplete rows. The new consolidated view contains 500 unchanged complete cases, 864 complete comparisons and 136 incomplete comparisons (1,364 complete vectors). All 24 new raw histories re-extract and all 24 new vectors were independently recounted; 668 saved response fingerprints were checked. Every former complete row, label, cutoff and historical result is preserved. The 160 observed counters imply at least 953,129 page requests (over eleven continuous days at one request per second), with a maximum history of 5,945,884 transactions. Collection is stopped and the lease is idle. Two interrupted consumed page requests remain explicit, without automatic retry. One complete orphan page response was recovered offline. Remaining work needs durable memory-bounded streaming execution and a separately pinned continuation; do not rerun this stopped pass. No model or split. The prior network-error automation remains disabled.

Latest artifacts: `research/coldcard/comparison_extended_20261031_164508/`. Older counts below are historical.


**31 October 2026 UTC — Verified final network recovery: 41 new attempts: 33 complete, eight bounded-incomplete and zero network errors. Combined: 500 unchanged complete cases, 840 complete and 160 bounded-incomplete comparisons; 1340 complete vectors. Network gaps: 0. All previous 200 pass entries and older complete/incomplete rows remain unchanged. The old 200 raw responses are unavailable locally; their fingerprints/normalized evidence and earlier audits are preserved. All available new responses re-extract; complete new vectors were independently recounted. Fourteen predictors, cutoff and unknown labels are unchanged. No model/split. Lease idle. Bounded-incomplete histories require a separate coverage decision.**

Older counts below are historical.


**Verified continuation — 31 October 2026 UTC:** the next five batches saved 100 new attempts: 89 complete, 11 bounded-incomplete, zero network errors. The current consolidated 1,500-row view contains 500 unchanged complete cases, 807 complete comparisons, 152 incomplete comparisons and 41 pending comparisons (1,307 complete vectors). All 200 raw responses in this pass re-extract; all 89 new complete vectors were independently recounted. The first 100 checkpoint is preserved in `comparison_retry_20261031_0300/milestone_batch_0005`. The lease is idle. Resume the same non-denied pass only over `comparison_0960`–`comparison_1000`, after lease/lock and due-time checks and one ordinary source-counter GET. Do not repeat complete/incomplete results or consumed markers. Fourteen predictors, cutoff and unknown labels remain unchanged; no model/split. Older progress paragraphs below are historical.


## Current priority

**Latest verified bounded collection:** after reconciliation of the expired lease
and the newer stopped checkpoint, the saved four-hour cooldown was honored.
[The successor](research/coldcard/comparison_retry_20261031_0300/README.md)
collected five batches: **100 attempted, 90 complete, ten incomplete, no errors**.
All 100 raw responses re-extract; all 90 complete vectors were independently
recounted. The previous stopped pass's 122 vectors were also independently checked.
The combined view has **500 unchanged complete cases, 718 complete comparisons,
141 incomplete comparisons and 141 pending**, with zero latest comparison errors.
There are 1,218 complete feature vectors among 1,500 selected rows. All earlier
outcomes/labels remain intact. The lease is idle; no model/split is fitted.
Earlier counts and failed-task accounts below remain historical.

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
  