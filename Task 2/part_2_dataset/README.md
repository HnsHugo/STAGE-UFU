# Part 2 — Build and understand the dataset

**Supplemental coverage — 31 October 2026 UTC:** Supplemental coverage recovered 24 complete comparison histories from the 160 previously bounded-incomplete rows. The new consolidated view contains 500 unchanged complete cases, 864 complete comparisons and 136 incomplete comparisons (1,364 complete vectors). All 24 new raw histories re-extract and all 24 new vectors were independently recounted; 668 saved response fingerprints were checked. Every former complete row, label, cutoff and historical result is preserved. The 160 observed counters imply at least 953,129 page requests (over eleven continuous days at one request per second), with a maximum history of 5,945,884 transactions. Collection is stopped and the lease is idle. Two interrupted consumed page requests remain explicit, without automatic retry. One complete orphan page response was recovered offline. Remaining work needs durable memory-bounded streaming execution and a separately pinned continuation; do not rerun this stopped pass. No model or split. The prior network-error automation remains disabled.

Latest artifacts: `research/coldcard/comparison_extended_20261031_164508/`. Older counts below are historical.


**31 October 2026 UTC — Verified final network recovery: 41 new attempts: 33 complete, eight bounded-incomplete and zero network errors. Combined: 500 unchanged complete cases, 840 complete and 160 bounded-incomplete comparisons; 1340 complete vectors. Network gaps: 0. All previous 200 pass entries and older complete/incomplete rows remain unchanged. The old 200 raw responses are unavailable locally; their fingerprints/normalized evidence and earlier audits are preserved. All available new responses re-extract; complete new vectors were independently recounted. Fourteen predictors, cutoff and unknown labels are unchanged. No model/split. Lease idle. Bounded-incomplete histories require a separate coverage decision.**

Older counts below are historical.


**Verified continuation — 31 October 2026 UTC:** the next five batches saved 100 new attempts: 89 complete, 11 bounded-incomplete, zero network errors. The current consolidated 1,500-row view contains 500 unchanged complete cases, 807 complete comparisons, 152 incomplete comparisons and 41 pending comparisons (1,307 complete vectors). All 200 raw responses in this pass re-extract; all 89 new complete vectors were independently recounted. The first 100 checkpoint is preserved in `comparison_retry_20261031_0300/milestone_batch_0005`. The lease is idle. Resume the same non-denied pass only over `comparison_0960`–`comparison_1000`, after lease/lock and due-time checks and one ordinary source-counter GET. Do not repeat complete/incomplete results or consumed markers. Fourteen predictors, cutoff and unknown labels remain unchanged; no model/split. Older progress paragraphs below are historical.


**Latest verified source collection:** the bounded successor saved 100 attempts: 90 complete, ten incomplete and no errors. The current 1,500-row view retains 500 unchanged complete cases, 718 complete comparisons, 141 incomplete comparisons and 141 pending, with zero latest comparison errors. See [current retry](../research/coldcard/comparison_retry_20261031_0300/README.md). Older counts below describe preserved historical units. No model/split or label promotion.

[Previous: Part 1](../part_1_case_study/README.md) · [Main path](../README.md) · [Next: Part 3](../part_3_classifier/README.md)

## Goal

Know what one row represents, where labels come from and which features a classifier receives.

**Address dataset stage:** the [source registry](../research/coldcard/source_registry_20261027/README.md)
is now built: 500 candidate-day source addresses / 1,324 input observations, plus
five later addresses retained separately. Independently verified compromise/hardware labels remain
unknown; the transaction corpus below still describes a different observation
unit. The [pre-payment pilot](../research/coldcard/prepayment_pilot_20261027/README.md)
now supplies fourteen cutoff-safe features for eight complete source histories;
the [multi-input extension](../research/coldcard/multiinput_pilot_20261028/README.md)
adds four more complete histories with unchanged definitions. The
[resumable cohort](../research/coldcard/source_cohort_20261028/README.md) finished with
473 complete histories, 24 retained errors, 3 incomplete histories and 0 pending sources. All 500 were attempted under that original protocol. See [Alignment](../ALIGNMENT.md).

The separate [supplemental recovery](../research/coldcard/source_cohort_recovery_20261029/README.md)
now provides **500 complete, 0 errors, 0 incomplete and 0 pending** under documented larger bounds.
The original protocol result remains unchanged. Independently verified labels and suitable
controls remain missing; see the recovery's per-source eligibility and evidence review.


The [external case corroboration](../research/coldcard/source_corroboration_20261030/README.md)
provides a new `source_attributed` relationship layer for all 500 sources, with
matching payments and input amounts. This layer is retrospective evidence;
keep it separate from pre-payment predictors and verified compromise/device labels.


The [first-person report layer](../research/coldcard/owner_report_adjudication_20261030/README.md)
adds one sourced loss/Coldcard declaration for `cohort_0002`. Reported positives,
verified labels, device origin and signing-device identity remain distinct.

The [consolidated source view](../research/coldcard/source_dataset_20261030/README.md)
now provides one pinned, reproducible 500-row dataset with all fourteen prior-block
features and separate evidence/outcome fields. Its report describes distributions,
missingness and the one partial reference spend. Use only `features` as predictors;
identifiers, case evidence, owner reports and reference-payment outcomes are excluded.

The [same-block comparison selection](../research/coldcard/source_comparison_selection_20261030/README.md)
now fixes 1,000 additional source identifiers for the exploratory core-membership
study. These are selected input addresses, not recipient controls or certified
legitimate addresses. All earlier collection and recovery snapshots are preserved.
After the configured background task failed to execute successfully, the
[foreground successor](../research/coldcard/comparison_retry_20261030_2133/README.md)
retrieved its [first 100 sources](../research/coldcard/comparison_retry_20261030_2133/milestone_batch_0005/README.md):
85 complete, 15 incomplete, zero errors. All 100 raw responses re-extract.
The saved combined view retains 500 unchanged complete cases, 591 complete
comparisons, 128 incomplete comparisons, one latest known error and 280 never
attempted. Exactly 1,091 rows have fourteen strictly prior-block predictors;
unavailable vectors stay null. Every earlier vector, outcome and unknown label
is preserved. The remaining 281 sources are continued directly. Background
execution is not verified and no model/split is fitted.

## Inputs and coverage

The supplied corpus contains 98 selected blocks and 493,571 unique transactions. It is not the entire blockchain or the entire history of every address. The saved feature CSV is supplied separately and identified by SHA256; [Data access](../DATA_ACCESS.md) lists the required inputs.

| Relation recorded in the feature corpus | Rows | Interpretation |
| --- | ---: | --- |
| Source-attributed consolidation | 5 | Linked to the case by an external investigation |
| Direct-parent candidate | 1,070 | Funding relation to a source-attributed transaction |
| Unattributed | 492,496 | Unknown relation; not certified legitimate |

There are 98 coinbase transactions. The grouped classifier excludes coinbase and the five consolidations, leaving 493,468 rows. The course exercise uses a different, smaller sample and a different payment-to-address target.

## Three main-path feature sets — keep their units separate

- **Source-address dataset, 14 features:** prior-block transaction/receipt/spend counts, output counts, integer amounts, balance, active blocks, activity spans/ages and median historical spending fee rate. One row is an address; this is the current address-model input view.
- **Course exercise, 10 features:** size (bytes), weight (weight units), fee (satoshis), output sum/minimum/maximum/mean/population standard deviation (satoshis), input count and output count. The course slide's `v` is interpreted as output values; this interpretation is documented.
- **Extended Coldcard experiment, 16 features:** counts, address-count/missingness fields, input/output totals, fee, virtual size, fee rate, version, lock time and output statistics. These are transaction features, not the 22-feature Real-CATS address profiles.

## Read and inspect

- [Feature definitions and descriptive checks](../research/coldcard/FEATURE_ANALYSIS.md).
- [Saved corpus manifest](../research/coldcard/inputs_20261008/manifest.json).
- [Label protocol](../research/coldcard/LABEL_PROTOCOL.md).
- [Dataset audit](../research/coldcard/grouped_results_20261008/dataset_audit.json).

## Code

[extract_features.py](../research/coldcard/extract_features.py), [extract_candidate_groups.py](../research/coldcard/extract_candidate_groups.py) and [audit_dataset.py](../research/coldcard/audit_dataset.py) implement extraction, grouping and checks. From the repository root:

```bash
python "Task 2/research/coldcard/audit_dataset.py" \
  /path/to/transactions.csv.gz /path/to/manifest.json /path/to/candidate_groups.json
```

The audit checks the supplied version. A genuinely new dataset requires its own documented provenance and experiment; do not replace a checksum merely to bypass validation.

## What to explain

“The labels describe observed relationships to this case. Transaction IDs, relation labels and block metadata are not used as classifier predictors. The feature units and coverage are explicit.”
