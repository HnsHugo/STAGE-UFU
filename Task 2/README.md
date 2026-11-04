# Task 2 — Hardware-wallet case studies and Bitcoin transaction analysis

The [four-page frozen transfer supplement](source_transfer_study_20261104/README.md) now provides checked English methods/results, two LaTeX fragments and an Overleaf import folder. It preserves the limited proxy-transfer result and all earlier model/data outputs; the original article is unchanged.

The latest [frozen CryptoBilis source-proxy evaluation](research/external_cases/cryptobilis_frozen_transfer_20261104_215520/README.md) scores exactly 275 eligible vectors without refitting: membership F1 0.629834, precision 0.966102 and recall 0.467213. Inactivity ranking has higher AP (0.854026 vs 0.688142). All 366 selections, 54 quarantined complete comparisons and 37 bounded prefixes are retained; all excluded sources remain unscored.

## Current source-address result — 2 November 2026

Read the [source-address research report](source_address_study/README.md) or its
[five-page PDF](source_address_study/source_address_study.pdf). It explains the
500 core sources, 1,000 fixed comparisons, fourteen prior-block predictors and
122 unavailable comparison vectors. The frozen membership tree uses 1,033
training / 111 validation / 234 test addresses in 918 observed-link components.
Test membership F1 is 0.989796 (97 TP, 135 TN, 1 FP, 1 FN). Inactivity alone also
separates the cohort strongly. This is retrospective, complete-case development
on one incident, with unknown independently verified compromise/device labels.

[LaTeX fragments and integration instructions](source_address_study/README.md#article-integration)
are ready for the supplied article's `Our Work` and `Results` sections. The
original article files and live Overleaf project were not modified. The model,
scores and previous scientific results are unchanged by the write-up. Collection
is closed and automation remains disabled. Older collection entries below are
historical; use this report and [Project status](PROJECT_STATUS.md) for current work.

The [CryptoBilis bounded acquisition and final audit](research/external_cases/cryptobilis_reference_prefix_20261104_201345/README.md)
now finalize all 366 fixed selections: 329 strict prior-prefix vectors (122 source
candidates / 207 comparisons), 37 bounded-incomplete comparisons without vectors,
and no network/unattempted sources. All raw tails and vectors reproduce; 2,262
response fingerprints and 19 batch snapshots verify. Source compromise/device
labels remain unknown, with current full histories outside this prefix audit.
Part 5 has completed the overlap/eligibility audit and frozen external inference.
The limited proxy-transfer result and fixed-rule errors are documented above;
the existing Coldcard model is unchanged. The next unit is the article write-up.

## Historical collection progress

**Validated pre-cutoff recovery — 31 October 2026 UTC:** The anchored pre-cutoff method matched every prior transaction and all fourteen predictors for eight full-history controls across all four blocks. Application to 136 unfinished comparisons then saved 37 results: eight complete prior prefixes and 29 bounded-incomplete; HTTP429 stopped two already-started requests, leaving 99 sources without a final prefix result. All eight new vectors were independently recounted, all 37 raw tails re-extract and 621 saved response fingerprints verify. The explicit pre-cutoff feature view has 500 complete case vectors and 872 comparison vectors, with 128 comparison vectors unavailable. Full-current-history comparison statuses remain 864 complete and 136 incomplete. Labels, cutoffs, all 1364 previous vectors and baseline bytes are preserved. A pre-cutoff cursor audit is separately labeled from full-current-history counter reconciliation. No model/split. The lease is idle and no provider request is allowed before 2026-11-01T06:25:21.786387+00:00. Two HTTP429 records and all successful pages are preserved. Resume only a separately pinned successor over the 99 network gaps; retain the 29 bounded-incomplete outcomes.

Latest artifacts: `research/coldcard/reference_tail_coverage_20261031_221432/`; exact resumption: `resume_checkpoint.json` in that folder. Older progress entries below are historical.


**Supplemental coverage — 31 October 2026 UTC:** Supplemental coverage recovered 24 complete comparison histories from the 160 previously bounded-incomplete rows. The new consolidated view contains 500 unchanged complete cases, 864 complete comparisons and 136 incomplete comparisons (1,364 complete vectors). All 24 new raw histories re-extract and all 24 new vectors were independently recounted; 668 saved response fingerprints were checked. Every former complete row, label, cutoff and historical result is preserved. The 160 observed counters imply at least 953,129 page requests (over eleven continuous days at one request per second), with a maximum history of 5,945,884 transactions. Collection is stopped and the lease is idle. Two interrupted consumed page requests remain explicit, without automatic retry. One complete orphan page response was recovered offline. Remaining work needs durable memory-bounded streaming execution and a separately pinned continuation; do not rerun this stopped pass. No model or split. The prior network-error automation remains disabled.

Latest artifacts: `research/coldcard/comparison_extended_20261031_164508/`. Older counts below are historical.


**31 October 2026 UTC — Verified final network recovery: 41 new attempts: 33 complete, eight bounded-incomplete and zero network errors. Combined: 500 unchanged complete cases, 840 complete and 160 bounded-incomplete comparisons; 1340 complete vectors. Network gaps: 0. All previous 200 pass entries and older complete/incomplete rows remain unchanged. The old 200 raw responses are unavailable locally; their fingerprints/normalized evidence and earlier audits are preserved. All available new responses re-extract; complete new vectors were independently recounted. Fourteen predictors, cutoff and unknown labels are unchanged. No model/split. Lease idle. Bounded-incomplete histories require a separate coverage decision.**

Older counts below are historical.


**Verified continuation — 31 October 2026 UTC:** the next five batches saved 100 new attempts: 89 complete, 11 bounded-incomplete, zero network errors. The current consolidated 1,500-row view contains 500 unchanged complete cases, 807 complete comparisons, 152 incomplete comparisons and 41 pending comparisons (1,307 complete vectors). All 200 raw responses in this pass re-extract; all 89 new complete vectors were independently recounted. The first 100 checkpoint is preserved in `comparison_retry_20261031_0300/milestone_batch_0005`. The lease is idle. Resume the same non-denied pass only over `comparison_0960`–`comparison_1000`, after lease/lock and due-time checks and one ordinary source-counter GET. Do not repeat complete/incomplete results or consumed markers. Fourteen predictors, cutoff and unknown labels remain unchanged; no model/split. Older progress paragraphs below are historical.


**Latest verified source collection:** the bounded successor saved 100 attempts: 90 complete, ten incomplete and no errors. The current 1,500-row view retains 500 unchanged complete cases, 718 complete comparisons, 141 incomplete comparisons and 141 pending, with zero latest comparison errors. See [current retry](research/coldcard/comparison_retry_20261031_0300/README.md). Older counts below describe preserved historical units. No model/split or label promotion.

**Start with Parts 1–4.** They explain the Coldcard coursework in order. Part 5 describes the next cross-case work. The supplementary benchmarks are preserved but are currently paused.

**Current alignment:** [Professor instructions, verified progress and next task](ALIGNMENT.md).
The transaction exercise is completed. The [source-address evidence registry](research/coldcard/source_registry_20261027/README.md)
now separates 500 candidate-day addresses from five later sources, with exact
outpoint links and unknown compromise/device labels. The
[pre-payment pilot](research/coldcard/prepayment_pilot_20261027/README.md) has
computed fourteen prior-block features on eight complete source histories.
The [multi-input extension](research/coldcard/multiinput_pilot_20261028/README.md)
adds four sources with the same extractor. The
[resumable cohort](research/coldcard/source_cohort_20261028/README.md) finished with
473 complete histories, 24 retained errors, 3 incomplete histories and 0 pending sources. All 500 sources were attempted under that original protocol.
The separate [supplemental recovery](research/coldcard/source_cohort_recovery_20261029/README.md)
now provides **500 complete, 0 errors, 0 incomplete and 0 pending**, preserving the original result.
Independently verified compromise/device labels and target-matched controls remain absent.
The [consolidated source view](research/coldcard/source_dataset_20261030/README.md)
now joins all 500 unchanged fourteen-feature records and their distinct evidence
tiers, with descriptive findings. The [comparison design and selection](research/coldcard/source_comparison_selection_20261030/README.md)
now add a frozen sample of 1,000 same-block input sources for an explicit
exploratory core-membership study. Every earlier collection/recovery is preserved.
The configured hourly task had no recorded scheduled execution; immediate/control
attempts failed without a detailed cause. The
[foreground successor](research/coldcard/comparison_retry_20261030_2133/README.md)
actually resumed collection after a normal HTTP 200 check. Its
[first-100 milestone](research/coldcard/comparison_retry_20261030_2133/milestone_batch_0005/README.md)
has 85 new complete histories and zero errors. The saved 1,500-row view retains
500 unchanged complete cases, 591 complete comparisons, 128 incomplete
comparisons, one latest known error and 280 never attempted. The remaining 281
sources are continued directly under the shared lease. Background execution
remains unverified; no model/split or label promotion. All 86 source-path tests
previously passed against the unchanged collector/extractor.
The [external corroboration](research/coldcard/source_corroboration_20261030/README.md)
now provides a source-attributed case layer for all 500 addresses, with exact
agreement against two published reconstructions. Individual victim/device
confirmation remains distinct from that case association.
The [first-person report review](research/coldcard/owner_report_adjudication_20261030/README.md)
adds one exact owner-reported loss/Coldcard association for `cohort_0002`, kept
separate from verified labels and the unchanged other 499 sources.
Collector ranking remains a preserved supporting experiment, not the central
objective or a substitute for that address dataset.

## The main learning path

| Part | Question | What to open |
| --- | --- | --- |
| [Part 1 — Case study and fund flows](part_1_case_study/README.md) | What happened in the observed transactions, and where did the funds go? | Financial report and parent coverage |
| [Part 2 — Dataset and features](part_2_dataset/README.md) | What data did we collect, and what does each variable mean? | Feature definitions, labels and integrity checks |
| [Part 3 — Interpretable classifiers](part_3_classifier/README.md) | What does each separate transaction/address classifier learn? | The frozen source-membership tree and historical 100 + 100 exercise |
| [Part 4 — Validation and limitations](part_4_validation/README.md) | What do the fixed held-out results and errors establish? | Source-membership metrics, attrition and historical grouped transaction results |
| [Part 5 — Additional cases and generalization](part_5_cross_case/README.md) | How should another hardware-wallet-related case be added? | Evidence requirements and work still pending |

The target address is `bc1qnk4zh9qcnap2mycp56qjrgza3cc8ylrh8fecp0`. A relationship to this case is not proof of theft or hardware-wallet use. Cold storage, hardware signing and illicit activity are different properties.

## Results to understand first

1. [Source-address study](source_address_study/README.md): 1,378 available vectors; frozen membership test F1 0.989796; one incident and 122 excluded comparisons.
2. [Financial analysis](research/coldcard/case_flows_20261015/CASE_FLOWS.md): observed receipts and spending, not a certified stolen total.
3. [Classroom exercise](research/coldcard/COURSE_EXERCISE.md): 60/60 on the small same-address sample test; this does not establish cross-case generalization.
4. [Historical grouped transaction validation](research/coldcard/GROUPED_EXPERIMENT.md): 874/1,070 candidate relations recovered, 1,072 alerts on unattributed background, and substantial variation across groups.

These are different experiments with different targets and protocols. Their scores should not be combined.

## Where things live

| Directory or document | Purpose |
| --- | --- |
| `part_1_*` to `part_5_*` | Short explanations in the order to learn and present the project |
| [research/](research/README.md) | Working scripts, case evidence and saved Coldcard results |
| [supplementary/](supplementary/README.md) | Real-CATS, Elliptic++ and the earlier wallet-storage pilot; outside the current main path |
| [verification/](verification/README.md) | Historical execution evidence and reorganization checks |
| [Project status](PROJECT_STATUS.md) | Completed, partial and blocked work |
| [Alignment](ALIGNMENT.md) | Reconciled Teams, Overleaf and meeting requirements; current source-first priority |
| [Requirements](REQUIREMENTS.md) | Original course requirements and later research notes |
| [Reproducibility](REPRODUCIBILITY.md) | Commands, dependencies and the offline demonstration |
| [Data access](DATA_ACCESS.md) | Files committed to Git versus separately supplied datasets |
| [Migration guide](docs/MIGRATION.md) | Where the old folders moved |

Read a report before opening its code. `.md` files explain the work, `.py` files run it, `test_*.py` files verify it, `.json` files retain detailed results, and `tree.txt` files show readable rules. Dated result files are historical records, not separate projects.

Need help with the terminology? Start with [Which model is which?](docs/MODEL_GUIDE.md) and the [plain-English glossary](docs/GLOSSARY.md).

## Quick checks

Run from the repository root:

```bash
python "Task 2/check_repository.py"
python "Task 2/run_demo.py"
```

The first command checks local documentation links, Python syntax and unchanged saved artifacts. The demo reports missing external inputs explicitly; it does not retrain a model. See [Reproducibility](REPRODUCIBILITY.md) for all test suites.

**Current direction:** develop the Coldcard source-address dataset from the
completed graph registry, then the classifier and compatible CryptoBilis extension.
Destination tracing supports this sequence. Keep historical models and results
unchanged; Ivan's missing code does not prevent building the source registry.
