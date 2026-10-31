# Foreground comparison retry — 30 October 2026, 21:33 UTC

The scheduled 18:08 São Paulo check had no recorded execution when inspected
at 21:29 UTC. A requested immediate automation run then failed (started 21:30:39,
completed 21:30:47 UTC), with no detailed cause or result returned. Automation
configuration is therefore not evidence of successful execution. A normal
source-counter request on the original route returned HTTP 200 at 21:33 UTC,
after the recorded two-hour cooldown.

This [protocol](../source_comparison_retry_protocol_20261030_2133.json) selects
exactly 381 remaining network gaps and pins all four prior comparison passes.
All 506 complete and 113 bounded-incomplete earlier results are excluded. The
14 predictors, strict prior-block cutoff, source/reference identities and unknown
labels are unchanged. The same provider/route/TLS, two workers, one global
request per second, sixteen pages and fifteen-second timeouts remain. The first
403/429 stops scheduling and preserves started attempts. No internal retry,
replacement, split or model. Actual results come from saved checkpoints.

The [first-100-source milestone](milestone_batch_0005/README.md) records five
verified batches: 85 complete, 15 incomplete and no errors; all 100 raw responses
re-extract. The combined view now has 591 complete comparisons and 500 unchanged
cases. Foreground collection continues the remaining 281 identifiers. The second
automation control test also failed without a detailed cause/result, so working
background execution is not claimed.

## Final stopped result

The foreground fallback attempted **142 sources**: **122 complete, 18 incomplete,
two HTTP429 errors and 239 pending**. The last planned batch stopped after its
two started requests failed; the remaining eighteen were not started. The error
IDs are `comparison_0760` and `comparison_0761`. All 140 successful raw responses
re-extract; see [collection audit](collection_audit.json) and
[stop record](collection_stop.json). The first-100 milestone is unchanged.

The [combined address view](address_dataset.json.gz) and
[summary](combined_summary.json) retain all 1,500 selected sources and every pass
outcome.

| Population | Complete | Incomplete | Latest error | Never attempted |
| --- | ---: | ---: | ---: | ---: |
| Coldcard case sources | 500 | 0 | 0 | 0 |
| Fixed comparisons | 628 | 131 | 2 | 239 |

There are 1,128 complete fourteen-feature vectors. All 506 earlier complete and
113 earlier incomplete comparisons remain unchanged, as do the 500 case vectors
and their separate owner-report/evidence tiers. Complete comparisons by reference
block are 99, 174, 286 and 69. Unavailable predictors stay null; unknown labels
remain unknown. No model/split is created.

The 241 remaining network gaps are `comparison_0760`–`comparison_1000`. The
collector is stopped and its lease cleared. New requests must wait until at least
01:51:56 UTC on 31 October (22:51:56 São Paulo on 30 October), doubling the previous
two-hour delay. A longer Retry-After would prevail; none was supplied. The 131
bounded-incomplete histories require separate coverage work.

The first configured scheduled task and its immediate tests failed without a
detailed reason/result. It was paused, preserving its history. A new hourly task
was created and tested, but that test failed too. Working background collection
is therefore not established; an enabled task or accepted run request is not
proof of successful execution. The replacement remains configured with the saved
backoff and preservation rules. See [automation diagnostics](../comparison_access_retries_20261030/automation_replacement_test_20261030.json)
and [session verification](../../../verification/foreground_repair_stopped_20261030.json).
