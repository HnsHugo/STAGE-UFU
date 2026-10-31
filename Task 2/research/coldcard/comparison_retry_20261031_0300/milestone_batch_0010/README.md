# Bounded comparison retry — 31 October 2026 UTC

The expired published lease was reconciled with the newer local stopped checkpoint.
Its four-hour backoff was respected. One original-route source-counter check
returned HTTP200. This successor selects 241 remaining gaps, excluding all 628
complete and 131 incomplete previous comparisons. All predecessors are pinned.
The fourteen predictors, strict cutoff, references and unknown labels are unchanged.
At most five batches run with two workers, one global request/second, sixteen
pages and fifteen-second timeouts, stopping at the first403/429. No model/split.
Private raw plans/histories stay excluded. Existing unrelated working changes
(including a modified older milestone checkpoint) are preserved without staging.

## Verified bounded result

Five batches attempted 100 sources: 90 complete, ten incomplete and zero errors.
All 100 raw responses re-extract and all 90 complete vectors were independently
recounted directly from raw pre-cutoff transactions/outpoints. The preceding
stopped pass was also reconciled without repeating its attempts.

The [combined view](address_dataset.json.gz) and [summary](combined_summary.json)
retain 500 unchanged complete cases, 718 complete comparisons, 141 incomplete
comparisons and 141 pending comparisons, with no latest comparison errors. Every
older complete/incomplete result and label remains unchanged. No model/split.
The [completion record](bounded_completion.json) records checks and bounds.
The lease is released. Next work resumes this same non-denied protocol over its
remaining 141 IDs; do not retry any completed/incomplete or consumed attempt.

## Next five batches verified

The next 100 sources produced 89 complete and 11 bounded-incomplete histories,
without network errors. The first 100 results are byte-preserved in
[milestone_batch_0005](milestone_batch_0005/). All 200 raw responses re-extract;
the 89 new complete vectors were independently recounted. Combined totals are
500 unchanged complete cases, 807 complete comparisons, 152 incomplete and 41
pending comparisons. The fourteen predictors, strict cutoff and unknown labels
remain unchanged. No model/split. The lease is released.
[Completion record](bounded_completion_20261031_0357.json). Resume this same
non-denied pass for IDs comparison_0960 through comparison_1000 only.
