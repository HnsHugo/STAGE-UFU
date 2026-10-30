# Preserved comparison retry — 30 October 2026, 18:41 UTC

Hugo explicitly requested repeated resumption. The same original-route source
counter returned HTTP 200 after over ninety minutes since the prior HTTP 429.
The [protocol](../source_comparison_retry_protocol_20261030_1841.json) pins that
[check](../comparison_access_retries_20261030/access_20261030T184106Z.json), both
earlier recoveries and the original collection. Exactly 653 latest network gaps
are eligible; every complete/incomplete result is excluded. Original references,
strict prior-block cutoff, fourteen predictors and unknown labels are unchanged.

Collection uses the same provider/TLS/proxy route, two workers, one global request
start per second, sixteen pages and fifteen-second request bounds. A first new
403/429 stops scheduling; started attempts are retained. No source is automatically
retried within this pass. All earlier pass outcomes remain in the combined view.
No model or split is fitted. Actual results are read from saved checkpoints.

The immutable [first-four-batch milestone](milestone_batch_0004/README.md) records
80 attempts, 70 complete, ten incomplete and zero errors. Later root checkpoints
advance beyond that saved point. The [retry policy](../comparison_access_retries_20261030/README.md)
records the confirmed hourly task and the active collector lease; scheduled checks
skip this running collection. All 86 source-path tests pass, and both older
combined views still reproduce byte for byte after lineage support was extended.

A later [200-source milestone](milestone_batch_0010/README.md) retains ten batches:
174 complete, 26 incomplete and zero errors, with all 200 raw responses
re-extracted. The combined snapshot has 500 unchanged cases and 447 complete
comparisons. Every earlier milestone remains intact. Collection continued beyond
this point; no model or split was created.

## Final stopped result

The first new rate-limit response stopped scheduling after **274 attempts**:
**233 complete, 39 incomplete, two HTTP 429 errors and 379 pending**. Already
started attempts finished; the other six IDs in the final planned batch were
not started. All 272 raw responses re-extract; see [collection audit](collection_audit.json)
and [stop record](collection_stop.json). The two 429s are `comparison_0619` and
`comparison_0621`; `comparison_0620` completed before scheduling stopped.

The [combined address view](address_dataset.json.gz) and
[summary](combined_summary.json) retain every prior pass outcome.

| Population | Complete | Incomplete | Latest known error | Never attempted |
| --- | ---: | ---: | ---: | ---: |
| Coldcard case sources | 500 | 0 | 0 | 0 |
| Fixed comparisons | 506 | 113 | 101 | 280 |

Thus 1,006 of 1,500 selected rows have fourteen predictors. Every earlier case
vector and all 273 earlier complete/74 earlier incomplete comparisons remain
unchanged. All other feature vectors stay null. Compromise/device labels remain
unknown, with the original separate owner-report tier retained. No split or model
was created. Complete comparisons by reference block are 99, 174, 233 and zero;
this remaining coverage gap still blocks the planned fit.

The remaining network gaps total 381: two latest 429 errors and 379 pending in
this pass. Of the pending IDs, 99 retain older errors and 280 have never been
attempted. Pending status in a new pass never erases a prior error. The 113
bounded-incomplete histories need a separate coverage decision.

The collector is stopped and its published lease is cleared. The confirmed hourly
automation remains enabled under the [retry policy](../comparison_access_retries_20261030/retry_policy.json).
No new request is eligible before 21:07:49 UTC, two hours after the last refusal.
Repeated 429s increase backoff, a longer Retry-After prevails and a 403 pauses the
task. A distinct next pass must preserve this checkpoint; a denied resume performs
zero HTTP. See [session verification](../../../verification/comparison_retry_stopped_20261030.json).

Offline verification uses the same protocol with this directory:

```bash
python "Task 2/research/coldcard/collect_comparison_histories.py" verify \
  "Task 2/research/coldcard/source_comparison_retry_protocol_20261030_1841.json" \
  "Task 2/research/coldcard/comparison_retry_20261030_1841"
python "Task 2/research/coldcard/combine_comparison_histories.py" verify \
  "Task 2/research/coldcard/source_comparison_retry_protocol_20261030_1841.json" \
  "Task 2/research/coldcard/comparison_retry_20261030_1841"
```
