# Resumable Coldcard source cohort — updated 29 October 2026

## Current saved state: batch 7

Automatic continuation executed batches 6–7 on 29 October 2026:
**40 fixed source attempts**, **40 complete histories**,
0 errors and 0 incomplete histories. Each completed
batch was exported and verified before continuation. The runner stopped with
reason `time_budget` after 406.092 seconds; its soft
300-second budget is checked between batches, so an in-flight batch finishes.
All 112 earlier records, including their six failures, remained identical.
Two workers, the protocol, fourteen features and strict prior-block cutoff are
unchanged. No classifier was fitted, and failures were not retried or replaced.

| Cumulative source coverage | Actual count |
| --- | ---: |
| Fixed candidate cohort | 500 |
| Earlier histories reused | 12 |
| Complete histories / fourteen-feature vectors | **146** |
| Retained collection errors | 6 |
| Incomplete histories | 0 |
| Sources not yet attempted | **348** |

The prefixes contain **238 prior source/transaction observations** and
**235 distinct transaction references**.
There are 3 repeated observations
across source prefixes and 5 sources with prior spending. Shared
references and source IDs are retained in the execution record. This overlap
does not establish ownership; histories cannot be assumed independent.
Compromise/device labels remain unknown, all sources share one incident group,
and provider-counter reconciliation is not cryptographic inclusion verification.

Saved results: [checkpoint](batch_0007/checkpoint.json),
[features](batch_0007/features.json), [coverage](batch_0007/progress.json) and
[execution checks](../../../verification/source_cohort_automatic_from6_20261029.json).
The checks re-extracted 146 raw histories,
reproduced each new export offline, restored the exact latest state without raw
files or network, and verified preservation of all 112 earlier records.

## Saved batches

Counts below are cumulative snapshots; earlier artifacts are unchanged.

| Snapshot | Complete | Errors | Incomplete | Pending |
| --- | ---: | ---: | ---: | ---: |
| [Batch 1](batch_0001/progress.json) | 30 | 2 | 0 | 468 |
| [Batch 2](batch_0002/progress.json) | 50 | 2 | 0 | 448 |
| [Batch 3](batch_0003/progress.json) | 66 | 6 | 0 | 428 |
| [Batch 4](batch_0004/progress.json) | 86 | 6 | 0 | 408 |
| [Batch 5](batch_0005/progress.json) | 106 | 6 | 0 | 388 |
| [Batch 6](batch_0006/progress.json) | 126 | 6 | 0 | 368 |
| [Batch 7](batch_0007/progress.json) | 146 | 6 | 0 | 348 |

## Automatic continuation

The user requested faster progress on 29 October. The twenty-source unit is a
checkpoint boundary, not a scientific requirement to stop for another message.
`run-many` chains these original fixed batches in a single foreground command,
exports and verifies each completed batch, and preserves every source-level
atomic save. Concurrency stays at two workers; pagination, timeouts, ordering,
feature definitions and terminal-error handling stay unchanged.

```bash
python "Task 2/research/coldcard/source_cohort.py" run-many \
  "Task 2/research/coldcard/source_cohort_protocol_20261028.json" \
  "Task 2/research/coldcard/source_cohort_work_20261028" \
  --output "Task 2/research/coldcard/source_cohort_20261028" \
  --restore "Task 2/research/coldcard/source_cohort_20261028/batch_0007/checkpoint.json" \
  --max-batches 25 --max-seconds 300
```

The time budget is soft and checked between batches. An already started batch
finishes, so elapsed time can exceed the requested budget. Existing working state
wins over `--restore`. Completed exports are verified, never overwritten. An
interrupted export is recovered before the next batch. Errors stay terminal;
there is no automatic retry or reassignment. Use only one collector per working
directory. This command writes local checkpoints; Git publication remains a
separate verified operation, and no process is promised after a chat response.
See the [runner verification](../../../verification/source_cohort_runner_20261029.json).

## Historical first batch: 28 October 2026

This is the collection pipeline for all **500 candidate source addresses** in
the registry, rather than another pilot. It reuses the unchanged fourteen-feature
extractor and includes only blocks strictly before each reference-payment block.
It does not fit a classifier or establish hardware/compromise ground truth.

| Source coverage | Actual count |
| --- | ---: |
| Fixed candidate cohort | 500 |
| Earlier histories reused without API requests | 12 |
| New addresses in fixed batch 1 | 20 |
| New histories complete and eligible | 18 |
| Network timeouts retained as errors | 2 |
| Total complete source histories / vectors | **30** |
| Histories incomplete because of pagination/counters | 0 |
| Sources not yet attempted | **468** |

The two errors are `cohort_0019` and `cohort_0020`, both reported as
`URLError: <urlopen error timed out>`. They were not replaced or retried to make
the batch look complete. The denominator remains 500, and their feature vectors
remain null. There are 32 recorded sources: 30 complete and two errors.

Thirty eligible sources contain **41 prior address/transaction observations**.
One source has prior spending, unlike the first twelve-source pilots. Its
historical spending-transaction fee rate is 17 sat/vbyte; the others have no
historical spending-fee observations. This is an observed transaction property,
not a hardware signing-device or owner-policy attribution.

That source's gross receipts and reconstructed balance differ, illustrating why
these fields cannot be interchanged. The extractor reconstructs earlier UTXOs
from receipts and consumed outpoints; it does not use current spent flags or the
later collector-payment fee. All labels remain unknown, all records belong to
one incident group, and data coverage is not classification accuracy.

## Recovery and collection behavior

- The complete cohort and its SHA256 order are fixed by the
  [protocol](../source_cohort_protocol_20261028.json). Sources are not selected by
  outcomes, feature values or collection success.
- A batch contains at most **20 pending addresses**, selected and saved before
  requests. An interrupted batch keeps the same remaining source IDs on resume.
  A failed source occupies its original slot; no replacement is added.
- API use is bounded to two workers, four pages per source and eight seconds per
  request. With before/after counters this is at most 120 requests per new batch,
  and may be fewer after early errors. Large histories may remain incomplete.
- Each complete response is stored atomically, then the state is stored atomically
  after that source. A response saved just before an interrupted state write is
  recovered from the raw cache without downloading it again.
- Complete records are skipped on later runs. Errors/incomplete records are
  retained and are not retried automatically. A separate retry stage remains to
  be designed if needed; they must not silently become negatives or disappear.
- The old twelve records are imported with pinned manifest, feature and proof
  hashes. Their raw files are copied when locally available. Published prefix
  evidence also permits reuse when an old raw file is absent.
- A published checkpoint contains source metadata, audits, unknown labels,
  prefix evidence and features. It can restore working state even without raw
  files; raw byte-level reconstruction then requires the separately retained
  originals. Offline feature verification needs no network access.

Working state is mutable and ignored by Git under `source_cohort_work_20261028/`.
Published batch directories are immutable; the exporter refuses to overwrite
one. No original raw input or earlier result is changed.

## First-batch artifacts and verification

- [Batch 1 checkpoint](batch_0001/checkpoint.json): complete resumable state,
  source fingerprints, raw snapshot hashes/dates, failure reasons and prefix proofs.
- [Feature table](batch_0001/features.json): the 32 recorded sources, with 30
  vectors and two explicitly unavailable vectors; cutoff/group metadata and null
  labels are separate from the predictors.
- [Coverage summary](batch_0001/progress.json): exact coverage, provenance and limits.
- [Execution record](../../../verification/source_cohort_20261028.json): tests,
  offline reproduction, prefix-only restoration and historical-artifact checks.

Full raw address histories stay local in the ignored working directory. The
checkpoint includes normalized prior-block evidence, not new full address lists.
Hashed references do not guarantee anonymity. Provider-counter consistency is
not cryptographic inclusion verification or proof of independence/ownership.

Run from the repository root to verify the saved checkpoint offline:

```bash
python "Task 2/research/coldcard/source_cohort.py" verify \
  "Task 2/research/coldcard/source_cohort_protocol_20261028.json" \
  "Task 2/research/coldcard/source_cohort_20261028/batch_0007"
```

To process the **next** batch using existing working state:

```bash
python "Task 2/research/coldcard/source_cohort.py" run \
  "Task 2/research/coldcard/source_cohort_protocol_20261028.json" \
  "Task 2/research/coldcard/source_cohort_work_20261028" --limit 20

python "Task 2/research/coldcard/source_cohort.py" snapshot \
  "Task 2/research/coldcard/source_cohort_protocol_20261028.json" \
  "Task 2/research/coldcard/source_cohort_work_20261028" \
  --output "Task 2/research/coldcard/source_cohort_20261028/batch_0008"
```

If working state is missing, add
`--restore "Task 2/research/coldcard/source_cohort_20261028/batch_0007/checkpoint.json"`
to the `run` command. Use the latest checkpoint, not a stale one. `--limit 0`
restores/imports/validates state without requesting new histories. An existing
working state takes precedence over `--restore` and is never rolled back.

Seven added tests simulate interruption, an orphan response, terminal failure,
duplicate-request prevention, restored state without raw data, integrity failures,
non-overwriting exports and reuse of all twelve prior records without a network.

## One next unit

Use `run-many` to continue from `batch_0008` within an explicit soft
time/batch budget, then publish the completed unit. Reuse current state or the
latest checkpoint; preserve failures, frozen features and incident/label limits.
