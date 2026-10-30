# Comparison-source history collection — 30 October 2026

Collect the histories of the [fixed 1,000 same-block comparison sources](../source_comparison_selection_20261030/README.md)
and compute the same fourteen strictly prior-block predictors as the 500 case
sources. One row is an address, not a person or device. Operational core
membership is zero; theft and hardware labels remain unknown. No fitting takes
place in this collection unit.

## Current result: network blocked

| Fixed comparison selection | Sources |
| --- | ---: |
| Complete histories and fourteen-feature vectors | 40 |
| Incomplete histories, no feature vector | 12 |
| Request errors, no feature vector | 668 |
| Not attempted / pending | 280 |
| Total | 1,000 |

There were 720 source attempts in 36 fixed batches. Of the errors, **662 are
`URLError: Tunnel connection failed: 403 Forbidden`** and six are timeouts.
The first tunnel denial is `comparison_0059`. The original stop guard handled
direct HTTP 403/429 responses but missed urllib's HTTPS CONNECT refusal, allowing
later addresses to be attempted and recorded as failures. This defect is fixed:
tunnel refusals now stop collection at a denied batch, and a blocked checkpoint
cannot start new requests on resume. The failure results are retained unchanged.

An execution-session interruption left 15 finished attempt markers outside the
working checkpoint. They were recovered without HTTP, completing the 720 saved
outcomes. The remaining IDs `comparison_0721`–`comparison_1000` stay pending.
No failed address was silently retried or replaced. Seventy-three source-path
tests pass, including the tunnel-denial/resume regression.

All **52 saved raw responses** were re-extracted: 40 complete and 12 incomplete.
The original 500 case feature records are unchanged. The complete comparison
records contain 1,403 prior address/transaction observations (1,399 distinct
references); all forty are in reference block 960188. This severe temporal and
coverage attrition blocks the planned experiment; no model or split was created.

- [Coverage and raw re-extraction audit](collection_audit.json).
- [Network stop and guard correction](collection_stop.json).
- [Before/after provider counter evidence](history_counter_evidence.json.gz).
- [Execution verification](../../../verification/comparison_histories_20261030.json).

The network refusal needs to be resolved through an authorized restoration of
access before pending collection. Any further attempt on the 668 errors or twelve
incomplete rows must be a separately recorded recovery pass preserving this one.

The [collection protocol](../source_comparison_collection_protocol_20261030.json)
pins the public selection, exact public/private plan hashes, frozen extractor
and existing history/audit/checkpoint helpers. The [public plan](plan.json.gz)
contains only hashed identifiers, cutoffs and reference-input accounting. Private
addresses can be reconstructed from the four-block cache and checked against
those hashes before requests.

## Executed first batch

Batch 1 is saved and verified: 20 fixed attempts, 14 complete histories, six
incomplete histories, zero request errors and 980 pending sources. All twenty
raw responses were re-extracted without changing the 500 original case features.
See [the first-batch audit](first_batch_audit.json). These are coverage counts,
not model performance.

From batch 2, the [capacity precheck](capacity_optimization.json) retains
addresses with more than 400 provider-reported confirmed transactions as
incomplete without fetching history pages that cannot exhaust the sixteen-page
bound. Both counter reads are saved; no zero feature vector is created. The
first batch remains unchanged. This affects request effort, not complete-history
eligibility or the frozen feature extractor. Seventy-two source-path tests pass.

## Bounds and durable evidence

Use Blockstream, two workers, at most sixteen pages per address, fifteen seconds
per HTTP request and fixed batches of twenty. A source attempt contains the
before counter read, bounded pagination and after counter read. Stable matching
counters and an exhausted terminal page are required for complete history.
Incomplete/error results have no feature vector and are never replaced or
silently retried. No spent-status flags or reference-payment fees become predictors.

A durable attempt marker is written before HTTP. On restart, a complete saved raw
response is re-extracted offline; a started attempt with no raw response is
retained as an interrupted error. Pending sources whose worker had not started
remain pending. The operating-system lock prevents two collectors sharing the
working directory. An entire batch denied by HTTP 403/429 stops further requests
with the remaining sources pending.

Working state is saved after every source. Each completed batch has one immutable
`batch_NNNN.json.gz` delta. The latest checkpoint, all-source feature/status rows,
coverage by reference block and batch-hash index are regenerated and verified
before another batch starts. Completed exports interrupted during saving are
repaired before any new HTTP request. Published normalized prefixes reproduce
features without private raw caches; provider-counter completeness is not a
cryptographic inclusion proof.

## Run and verify

```bash
python "Task 2/research/coldcard/collect_comparison_histories.py" run-many \
  "Task 2/research/coldcard/source_comparison_collection_protocol_20261030.json" \
  "Task 2/research/coldcard/comparison_histories_20261030" \
  --work "Task 2/research/coldcard/source_cohort_work_comparison_histories_20261030" \
  --cache "Task 2/research/coldcard/source_cohort_work_comparison_20261030/blocks" \
  --max-batches 50
python "Task 2/research/coldcard/collect_comparison_histories.py" verify \
  "Task 2/research/coldcard/source_comparison_collection_protocol_20261030.json" \
  "Task 2/research/coldcard/comparison_histories_20261030"
```

`--restore` accepts a published compressed checkpoint if working state was lost;
completed/error/incomplete entries are not requested again. Run only one
collector per working directory. Source-path tests include interrupted attempts,
raw orphan recovery, no replacement, cross-provider reference amounts, raw/label/
feature tampering, exact offline restoration and the provider-denial stop.

The initial implementation passed 70 source-path tests; the capacity optimization
passed 72 and the tunnel-denial fix passes 73. These are software checks, not
collection accuracy or a count of valid histories. The current result is above.
