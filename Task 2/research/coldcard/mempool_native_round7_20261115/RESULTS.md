# Verified stopped checkpoint — 15 November 2026

The request to complete every remaining history is **unfinished**. The official
Coldcard feature view remains **1,445/1,500 complete**, with **55 missing rows**.
One additional complete prefix (`comparison_0877`) passes the independent data
checks but stays quarantined because its acquisition unit failed the timing
audit. No candidate is silently promoted.

This resumed session collected **461 HTTP200 responses**, zero HTTP failures,
**443 new native pages** and **11,037 prior-block address–transaction observations**.
Observations are not a global unique-transaction count. All successful data and
all 1,445 earlier complete vectors are preserved. No model fit or score occurred.

| Unit | Sources collected | HTTP200 | Full audit | New complete prefixes |
|---|---:|---:|---|---:|
| 1, preceding saved session | 2 | 104 | Passed | 0 |
| 2, this session | 3 | 156 | Passed | 0 |
| 3, this session | 3 | 156 | Passed | 0 |
| 4, this session | 3 | 149 | Failed timing; data verified separately | 1 quarantined |

Unit 4 records one UTC dispatch interval of **4.79656 seconds**, below the
existing **4.9-second audit threshold** for the nominal five-second spacing.
The original error remains [preserved](../mempool_native_round7_20261115_unit_04/audit_failure.json).
These timestamps do not distinguish an actual dispatch-spacing issue from a
host wall-clock correction; monotonic dispatch evidence was not recorded.
The [offline data audit](../mempool_native_round7_20261115_unit_04/offline_data_verification.json)
verifies fingerprints, cursor continuity, raw reconstruction, strict cutoffs,
independent feature recount and old-row/label invariants. It does **not** pass
the original operational audit or authorize promotion/continuation.

All **5,054 private evidence files** across the four units are saved, including
the stopped layer. The official view points to unit 3; the candidate view is
separate. All **103 historical/current locks** checked free, lease idle, provider
gate closed and no automatic/background task running. Units 5 and 6 were not
started; six selected histories remain unattempted in this campaign. The other
38 missing histories outside this selection remain retained.

The original pinned collectors/protocols stay unchanged. A new
[recorded runner](../recorded_mempool_resume.py) adds a 5.25-second monotonic
minimum, an explicit UTC guard, per-request clock evidence and correct handling
of failures before dispatch. **46 targeted tests pass**, including six timing
regressions. This new runner has not made a provider request and needs a distinct
pinned successor protocol, the usual fresh locks and published lease/readback.
It does not reopen the consumed scope or erase the failed audit. Existing user
API/GitHub authorization remains retained; the closed gate is operational.

[Verification](final_verification.json) · [Reproduce checkpoint verification](verify_final.py)
· [Exact progress and quarantine pointers](progress.json)
