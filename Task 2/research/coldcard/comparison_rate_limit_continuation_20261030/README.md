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
