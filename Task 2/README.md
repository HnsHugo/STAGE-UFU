# Task 2 — Hardware-wallet case studies and Bitcoin transaction analysis

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
| [Part 3 — The classroom classifier](part_3_classifier/README.md) | Can an interpretable tree recognize payments to the course address? | The 100 + 100 exercise and readable tree |
| [Part 4 — Validation and limitations](part_4_validation/README.md) | Does the result hold when related groups are kept apart? | Grouped results and simple baselines |
| [Part 5 — Additional cases and generalization](part_5_cross_case/README.md) | How should another hardware-wallet-related case be added? | Evidence requirements and work still pending |

The target address is `bc1qnk4zh9qcnap2mycp56qjrgza3cc8ylrh8fecp0`. A relationship to this case is not proof of theft or hardware-wallet use. Cold storage, hardware signing and illicit activity are different properties.

## Three results to understand first

1. [Financial analysis](research/coldcard/case_flows_20261015/CASE_FLOWS.md): observed receipts and spending, not a certified stolen total.
2. [Classroom exercise](research/coldcard/COURSE_EXERCISE.md): 60/60 on the small same-address sample test; this does not establish cross-case generalization.
3. [Grouped validation](research/coldcard/GROUPED_EXPERIMENT.md): 874/1,070 candidate relations recovered, 1,072 alerts on unattributed background, and substantial variation across groups.

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
