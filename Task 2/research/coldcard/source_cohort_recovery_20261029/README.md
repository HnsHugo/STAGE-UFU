# Supplemental Coldcard source-history recovery — 29 October 2026

## Executed requirement and observation unit

Recover the 27 unavailable histories in the exhausted original 500-source
cohort, preserving every original output. Each observation is a source address,
linked to its pinned reference payment. This is retrospective dataset
construction. Compromise, hardware seed origin and hardware signing at the event
are distinct targets; no verified labels or train/test split are created here.

## Prespecified changed collection bounds

The [recovery protocol](../source_cohort_recovery_protocol_20261029.json) pins
the original protocol/checkpoint hashes and the exact 24-error/3-incomplete
source selection before requests. It permits one supplemental attempt per
selected address, **16 pages instead of 4** and a **15-second request timeout
instead of 8**. Two workers, the provider, SHA256 source order, fourteen-feature
extractor and strict prior-block cutoffs stay unchanged. An empty terminal page
and stable matching provider counters remain mandatory. No replacement or
automatic repeat of a recovery failure is permitted.

The original four-page result remains **473 complete, 24 errors and 3 incomplete**.
The supplemental result is a different collection protocol and must be reported
as such. All 473 original complete checkpoint entries are copied unchanged into
the overlay. Earlier failures remain in their original checkpoint and in the
transition audit below.

## Actual result

The explicit pass attempted all **27** fixed sources in batches of **20 and 7**.
It produced **27 complete histories**, 0 errors and 0 incomplete histories in
420.582 seconds. The combined overlay has **500 complete, 0 errors, 0 incomplete and 0 pending**.
It contains 1445 prior source/transaction observations,
1431 distinct transaction references and
18 sources with prior spending. Repeated references are observed overlap;
they do not establish independent owners, victims or devices.

The historical spending-fee feature is missing for **482/500** complete
histories. Missing historical spending does not inherit the reference payment's
fee. See the [feature missingness/range profile](../../../verification/source_cohort_recovery_20261029.json).
Collection coverage is not classification accuracy. Provider counters do not
provide cryptographic inclusion proofs.

The three originally incomplete sources were checked as follows:

| Source | Transactions collected | Provider count before/after | Recovery status |
| --- | ---: | ---: | --- |
| `cohort_0191` | 110 | 110/110 | complete |
| `cohort_0432` | 92 | 92/92 | complete |
| `cohort_0435` | 227 | 227/227 | complete |

### Original-to-supplemental lineage

| Source | Original status | Supplemental status |
| --- | --- | --- |
| `cohort_0019` | error | complete |
| `cohort_0020` | error | complete |
| `cohort_0052` | error | complete |
| `cohort_0053` | error | complete |
| `cohort_0058` | error | complete |
| `cohort_0059` | error | complete |
| `cohort_0147` | error | complete |
| `cohort_0148` | error | complete |
| `cohort_0159` | error | complete |
| `cohort_0160` | error | complete |
| `cohort_0175` | error | complete |
| `cohort_0176` | error | complete |
| `cohort_0182` | error | complete |
| `cohort_0183` | error | complete |
| `cohort_0191` | incomplete | complete |
| `cohort_0294` | error | complete |
| `cohort_0295` | error | complete |
| `cohort_0369` | error | complete |
| `cohort_0370` | error | complete |
| `cohort_0373` | error | complete |
| `cohort_0374` | error | complete |
| `cohort_0381` | error | complete |
| `cohort_0382` | error | complete |
| `cohort_0416` | error | complete |
| `cohort_0417` | error | complete |
| `cohort_0432` | incomplete | complete |
| `cohort_0435` | incomplete | complete |

Original reasons and the complete fixed selection remain in the
[recovery audit](recovery_audit.json). Original historical snapshots are unchanged.
New raw histories stay in the ignored working directory; the published
checkpoints retain normalized prior-block evidence for offline reproduction.

## Verified artifacts

- [Combined checkpoint](batch_0002/checkpoint.json),
  [fourteen-feature rows](batch_0002/features.json) and
  [coverage](batch_0002/progress.json).
- [First twenty-source snapshot](batch_0001/progress.json).
- [Recovery/lineage audit](recovery_audit.json).
- [Per-source label eligibility](label_eligibility.json) and
  [reviewed evidence/required fields](../source_label_review_20261029.json).
- [Execution verification](../../../verification/source_cohort_recovery_20261029.json).

Checks re-extracted 27 new raw histories, reproduced both exports,
restored the exact final checkpoint offline without raw files or requests and
verified all 473 inherited complete entries. Earlier complete raw histories
are excluded from Git and were unavailable here; their normalized evidence and
feature rows were verified. Eighteen regression tests cover the cohort/recovery
path, including frozen input checks, source selection, old-result preservation,
resume and terminal-error retention.

## Label eligibility and remaining work

All 500 records retain unknown compromise/device labels. The focused
[evidence review](../source_label_review_20261029.json) supplies case-level
context, not individually adjudicated labels. Seed-generation device and
signing device at the relevant event must remain separate. No-report addresses
are not negatives. There are zero documented target-matched negative controls,
zero supervised-eligible records and only one incident group.

Next: adjudicate exact, dated address/payment assertions against the fields in
the evidence review, or explicitly define a different proxy target before any
experiment. Do not silently relabel these sources, present random within-case
splits as incident generalization, or fit a hardware/theft detector from the
collector relationship alone. No model was fitted or changed.

## Reproduction

From the repository root, offline:

```bash
python "Task 2/research/coldcard/source_cohort_recovery.py" verify \
  "Task 2/research/coldcard/source_cohort_recovery_protocol_20261029.json" \
  "Task 2/research/coldcard/source_cohort_recovery_20261029"
python "Task 2/research/coldcard/source_cohort_recovery.py" eligibility \
  "Task 2/research/coldcard/source_cohort_recovery_protocol_20261029.json" \
  "Task 2/research/coldcard/source_cohort_recovery_20261029"
```

The original execution command was:

```bash
python "Task 2/research/coldcard/source_cohort_recovery.py" run \
  "Task 2/research/coldcard/source_cohort_recovery_protocol_20261029.json" \
  "Task 2/research/coldcard/source_cohort_recovery_20261029" \
  --work "Task 2/research/coldcard/source_cohort_work_recovery_20261029"
```

Do not start a new work directory to repeat finished attempts. Reuse/restore
the saved final state for offline checks; any later collection unit needs its
own explicit selection, bounds and output.
