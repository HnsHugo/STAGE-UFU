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
