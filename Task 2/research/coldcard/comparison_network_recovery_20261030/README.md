# Comparison network recovery — 30 October 2026

Hugo requested resumption after the initial network block. A normal request to
the original Blockstream endpoint now returned HTTP 200; the saved
[access check](access_check.json) records that result. This is a separate,
user-authorized one-pass recovery, preserving all bytes of the
[initial collection](../comparison_histories_20261030/README.md).

The [recovery protocol](../source_comparison_network_recovery_protocol_20261030.json)
selects exactly 948 original source IDs: 668 network errors and 280 not-attempted
sources. The 40 complete originals remain unchanged, and twelve histories already
incomplete under the fixed bounds are excluded from this network-only recovery.
The [public plan](plan.json.gz) and its hashes preserve the original source,
reference-payment and block identities. No replacement or relabeling occurs.

Use the same two source workers, sixteen-page maximum, fifteen-second per-request
timeouts and unchanged fourteen-feature extractor. Optional persistent HTTPS uses
the original provider, system proxy configuration and verified TLS, with two
connections and a global maximum of three request starts per second. Connection
reuse changes transport cost, not history completeness or predictor definitions.
Install the optional dependency from `../requirements_collection.txt` if needed;
offline verification still uses standard-library Python.

The first denied HTTP 403/429 or HTTPS tunnel causes queued unstarted sources to
remain pending. Already-started attempts finish and are saved; partial-batch plans
remain explicit. A blocked saved run cannot silently issue new requests on resume.
The original 73 regressions plus recovery-selection, immediate-stop and transport
boundary checks passed before network collection.

```bash
python "Task 2/research/coldcard/collect_comparison_histories.py" run-many \
  "Task 2/research/coldcard/source_comparison_network_recovery_protocol_20261030.json" \
  "Task 2/research/coldcard/comparison_network_recovery_20261030" \
  --work "Task 2/research/coldcard/source_cohort_work_comparison_network_recovery_20261030" \
  --cache "Task 2/research/coldcard/source_cohort_work_comparison_20261030/blocks" \
  --max-batches 48
```

Completed batch deltas are immutable and verified before the next batch. Raw
histories and exact identifiers stay local; normalized prior-block evidence and
hashes are published. Results will be reported from actual checkpoints, never
inferred from the prepared plan. Compromise/device labels remain unknown and
no model is fitted in this collection step.

First executed recovery batch: twenty sources attempted, nineteen complete, one
incomplete and zero request errors. All twenty raw responses reproduce; see
[first-batch audit](first_batch_audit.json). The original pass is unchanged.

Final saved recovery result: **297 attempts, 233 complete, 62 incomplete, two
HTTP 429 errors and 651 pending**. The stop guard retained the other three
unstarted IDs in the last planned batch as pending. All 295 successful raw
responses reproduce; see [collection audit](collection_audit.json) and
[stop record](collection_stop.json). The first two reference blocks now have
complete comparison histories.

The [combined view](address_dataset.json.gz) retains all 1,500 selected sources:
500 complete cases plus 1,000 comparisons. At this snapshot, comparisons have
273 complete, 74 incomplete, 373 latest known errors and 280 never attempted.
Of the current recovery's 651 pending IDs, 371 retain original errors and 280
retain their never-attempted status; no old error is silently recoded as pending.
See [combined summary](combined_summary.json) for provenance and per-block counts.
A subsequent rate-limit continuation must be a distinct pinned pass, preserve
this stopped checkpoint, wait at least fifteen minutes and reduce the global
request rate to one per second. Neither a split nor a model has been created.
