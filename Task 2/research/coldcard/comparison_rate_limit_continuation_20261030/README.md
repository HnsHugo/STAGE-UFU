# Comparison cooldown continuation — 30 October 2026

This distinct user-authorized continuation preserves the entire
[initial pass](../comparison_histories_20261030/README.md) and
[first recovery](../comparison_network_recovery_20261030/README.md).
It selects exactly 653 latest errors/pending (`comparison_0348`–`comparison_1000`),
excluding all 273 complete and 74 bounded-incomplete earlier results. Original
references, fourteen predictors, strict prior-block cutoff and unknown
compromise/device labels are unchanged.

The [protocol](../source_comparison_rate_limit_continuation_protocol_20261030.json)
pins both earlier checkpoints and the saved HTTP 429 stop. It enforces at least
fifteen minutes after the last recorded 429 and reduces the global request rate
from three to one start per second. The previous responses did not preserve a
Retry-After header; future denial markers retain it when supplied. This is a
conservative local cooldown, not a claimed provider-prescribed interval. The
same provider, system proxy settings, verified TLS, two workers, sixteen-page
maximum and fifteen-second request timeouts remain. There is no provider/route
fallback and no automatic retry within this pass. Any new 403/429 stops scheduling
and retains unstarted sources as pending. A stopped saved pass cannot silently
resume. The old light-endpoint access check is historical; it is not new evidence
that the rate limit cleared. The first normal source attempt after cooldown
supplies that evidence, or stops the pass if still limited.

```bash
python "Task 2/research/coldcard/collect_comparison_histories.py" run-many \
  "Task 2/research/coldcard/source_comparison_rate_limit_continuation_protocol_20261030.json" \
  "Task 2/research/coldcard/comparison_rate_limit_continuation_20261030" \
  --work "Task 2/research/coldcard/source_cohort_work_comparison_rate_limit_continuation_20261030" \
  --cache "Task 2/research/coldcard/source_cohort_work_comparison_20261030/blocks" \
  --max-batches 33
```

Every completed batch is exported and verified before the next. No model or split
is created. Actual results are taken from saved checkpoints, never the plan.

## Executed result

Both already-started sources returned HTTP 429 again; the immediate stop guard
retained the other eighteen planned first-batch IDs as pending. **Two attempts,
zero complete, zero incomplete, two errors and 651 pending.** The responses
supplied no Retry-After value. See [stop record](collection_stop.json) and
[collection audit](collection_audit.json). No further pass was launched.

The [combined address view](address_dataset.json.gz) and
[summary](combined_summary.json) preserve all 1,500 selected rows, source identities,
cutoffs, fourteen-feature vectors, unknown labels and all three pass outcomes.

| Population | Complete | Incomplete | Latest known error | Never attempted |
| --- | ---: | ---: | ---: | ---: |
| Coldcard case sources | 500 | 0 | 0 | 0 |
| Fixed comparisons | 273 | 74 | 373 | 280 |

Of the stopped continuation's 651 pending IDs, 371 retain original errors and
280 have never been attempted. Pending in a later pass does not erase an earlier
error. Two other IDs retain the latest 429 result. All 40 original complete and
12 original incomplete comparisons are unchanged; the recovery's 233 complete
and 62 incomplete results also remain unchanged. The earlier 295 raw responses
were re-extracted; no successful response exists in this cooldown continuation.

Complete comparison counts by reference block are 99/126, 174/220, 0/336 and
0/318. This attrition prevents the planned exploratory fit. The 74 incomplete
full histories have null predictors; they require a separately justified coverage
decision rather than another network retry. No split or model was produced.
The collector is stopped; no background task is scheduled. Reassess permitted
access after a longer cooldown before any additional separately recorded pass.

Offline reproduction (no HTTP):

```bash
python "Task 2/research/coldcard/audit_comparison_histories.py" \
  "Task 2/research/coldcard/source_comparison_rate_limit_continuation_protocol_20261030.json" \
  "Task 2/research/coldcard/comparison_rate_limit_continuation_20261030" --verify
python "Task 2/research/coldcard/combine_comparison_histories.py" verify \
  "Task 2/research/coldcard/source_comparison_rate_limit_continuation_protocol_20261030.json" \
  "Task 2/research/coldcard/comparison_rate_limit_continuation_20261030"
```

All 85 source-path tests pass, including preservation across three passes,
unchanged labels/references, cooldown enforcement, reduced-rate bounds and
immediate denial stop. See [session verification](../../../verification/comparison_recovery_20261030.json).
