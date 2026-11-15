# Saved unit with failed operational timing audit

All three sources returned final collection outcomes: **149/149 HTTP200**, no
HTTP failure, **143 new native pages**, and **3,537 additional prior-block
address–transaction observations**. `comparison_0853` and `comparison_0892` remain
bounded-incomplete at 228 native pages. `comparison_0877` reaches terminal
pagination at 221 pages and passes independent UTXO/feature reconstruction.

The full original audit **failed**, because one saved UTC dispatch interval is
4.79656 seconds instead of the accepted minimum 4.9 seconds. No monotonic evidence
exists for that interval, so its cause remains undetermined. Preserve
[audit_failure.json](audit_failure.json); the original pinned auditor was not
relaxed or rewritten. The separate [data-only verification](offline_data_verification.json)
passes all data, cursor, cutoff, identity and feature invariants while explicitly
retaining the operational failure.

The candidate view contains 1,446 data-complete rows, including the one newly
complete prefix. It remains quarantined; **the official view stays at 1,445**.
All **1,385 private evidence files** are saved and fingerprint-verified. The
scope is closed, its permit removed, locks released and lease idle. No model,
score, new request, retry or automatic continuation follows this stopped scope.
See the [campaign result](../mempool_native_round7_20261115/RESULTS.md).
