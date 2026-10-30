# Spaced comparison retries — 30 October 2026

Hugo explicitly requested repeated resumption while preserving existing work.
The [18:41 UTC check](access_20261030T184106Z.json) returned HTTP 200 on the same
source-counter endpoint that had received HTTP 429. It is an access check, not a
new complete-history result. The distinct
[current pass](../comparison_retry_20261030_1841/README.md) preserves all earlier
protocols, checkpoints, outcomes and labels.

The [retry policy](retry_policy.json) defines hourly checks, a single source-counter
request only when due, a two-hour minimum after a new 429, increasing backoff up
to 24 hours and full respect for a longer server Retry-After. A held collector
lock skips the check. A new 403 stops and pauses the task; no alternate route,
provider, account or proxy is used. Successful collection remains bounded to the
original fourteen-feature protocol with one global request start per second.
Scheduled iterations may execute at most five batches before saving and publishing.
The task pauses once no network errors/pending IDs remain; incomplete full-history
coverage is a separate issue. No model is fitted.

The user's new request supersedes the earlier assistant-authored restriction to
one cooldown continuation. Every additional pass remains explicit, pinned and
separate; earlier results are never overwritten. The scheduling tool confirmed the enabled hourly task at 18:47 UTC. The public
policy records its title, schedule and activation time; private control identifiers
are not needed to reproduce collection.
