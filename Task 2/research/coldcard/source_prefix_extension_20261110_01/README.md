# Restored evidence and next bounded Coldcard extension, 10 November 2026

**Status: offline restoration completed; the new collection is prepared and has
not started.** This unit serves the latest coverage priority in
[ALIGNMENT.md](../../../ALIGNMENT.md). It preserves the 9 November closed scope,
all original vectors, both frozen transfer experiments and disabled automation.

The observation unit remains a decoded Bitcoin source address tied to its frozen
reference payment. The operational target is incident-source membership;
verified compromise, device and seed-origin labels remain unknown. The 14
predictors retain the strict block-height cutoff before each reference block.
There is no fitting, inference, new split, graph experiment or migration finding.

## Evidence actually recovered

The three-part 9 November archive was concatenated and verified against its
published combined SHA256. Its manifest and all **4,419 private files** verify.
Existing raw evidence and operational outcomes were preserved byte-for-byte.

A separately saved `coldcard_private_evidence_20261102_1508.tar.gz` is truncated:
71,041,024 observed bytes versus 73,387,033 published bytes, with a different
container hash and an interrupted tar stream. It is **not a verified archive**.
The original saved file remains unchanged; it must not be treated as a complete
backup or restored as trusted code/operational state.

Nevertheless, all **19 complete raw-tail members** from that continuation were
present before the truncation. Every member matches its independently published
checkpoint fingerprint. Re-extraction reproduces all 19 saved outcomes. The
2 complete prefixes are already included in the existing baseline; the other
17 remain bounded and supply no feature vector.

Canonical serialization of those raw tails reconstructs **all 332 historical
response bodies**: 19 anchors, 19 reference-status responses and 294 tail pages.
Every compressed response matches its separate published fingerprint; all
294 tail endpoint/cursor sequences also match. This recovers the missing bodies
without trusting incomplete trailing members or making a provider request.
Old ready/lease/lock flags were excluded. Raw evidence and addresses remain private.

See [cache_restoration_verification.json](cache_restoration_verification.json)
and [the independent verification](independent_preparation_verification.json).
The damaged container is still damaged; individually recovered evidence does
not certify its missing bytes. Earlier continuation caches not contained in
these archives remain unavailable locally.

## Prepared successor

[protocol.json](protocol.json) fixes exactly the next 20 unextended Coldcard IDs
declared by the previous resume checkpoint, `comparison_0140` through
`comparison_0236` with the exact intervening list retained in the protocol.
No complete prefix or source from the previous 20-source extension is selected.
The previous 16 outcomes bounded at 32 pages are not repeated.

The restored historical plans match the current view's source/payment hashes,
reference heights and block hashes. Eleven selected sources have a verified
anchor and a contiguous cached tail: nine have 16 pages, one has 14 and one has
8. The other nine lack usable anchored responses in the available archives.
**177 responses are reused: 11 references and 166 tail pages.** The separately
recovered 17 bounded sources are later IDs, available for future scopes rather
than substituted into this fixed batch.

| Maximum new request category | Count |
| --- | ---: |
| Single ordinary availability counter | 1 |
| Missing reference transactions | 9 |
| Tail pages, capped at 32 total per source | 474 |
| Fresh reference status after collection | 20 |
| Funding-transaction statuses, conservative input-slot bound | 21 |
| **Total maximum** | **525** |

This budget bounds this batch, not the requests required to exhaust all remaining
prefixes. Some already collected historical pages are absent from the available
archives and may require fresh requests in this distinct scope. Failed markers
are never copied or silently consumed again. See the per-source accounting in
[capacity_and_cache_audit.json](capacity_and_cache_audit.json) and fingerprints
in [offline_reuse_manifest.json](offline_reuse_manifest.json).

The protocol verifies 84 inherited predecessor pins and freezes **97 input pins**
in total. The baseline remains **1,382/1,500 Coldcard vectors and 329/366
CryptoBilis vectors**, with **155 unavailable prefixes**. Full-current-history
coverage and all unknown labels remain unchanged. No new vector is claimed.

## Execution gate and next action

No collector was started and no lease was acquired. Before any provider traffic,
hold the new local lock plus all declared historical locks, fetch the live
published retry policy, check cooldown and competing leases, then publish/read
back a fresh running lease for this exact protocol. Only then write a fresh
private permit and use the pinned original `run_scope.py` wrapper. Existing
operational flags must never be copied from a backup.

The first request must be one normal counter GET for the first fixed source.
Only HTTP200 allows collection. Keep the original Blockstream route, inherited
proxy, verified TLS, two workers, one global request start per second and 15s
timeouts. Stop new starts on the first 403/429; preserve Retry-After and the
existing backoff. No internal retry, provider/route/account/proxy/IP/TLS fallback
or automation enablement is authorized by this preparation.

After collection, use a separately verified successor audit with this **1,382**
vector baseline. The old audit hardcodes the older 1,378-vector baseline and must
not be reused unchanged. Verify raw tails, endpoint sequences, funding closure,
all preserved rows and new vectors before publishing any composed view. Recheck
overlap before updated-snapshot model work. The third-incident and graph/deep-
learning work retain their place in the supervision plan.

## Reproduction and validation

The three Python tools take explicit private paths. In a fresh working copy of
this scope, preserve these published outputs and use separate new output files
or a distinct successor directory; the tools refuse to overwrite a restoration
or prepared protocol. Reproducing the preparation in another workspace changes
the private lock-manifest fingerprint and requires a separately pinned protocol,
fresh live locks and a fresh published lease before any execution.

- `recover_cache.py PRIMARY_ROOT SUPPLEMENTAL_ARCHIVE RESTORED_WORK REPORT`
  verifies the primary cache and recovers only complete, individually pinned
  supplemental raw members. Its response reconstruction fails on any hash or
  endpoint mismatch.
- `prepare_scope.py PRIMARY_ROOT RESTORED_WORK NEW_WORK` writes the fixed private
  plan, validated reuse cache, historical lock list and public preparation.
- `verify_preparation.py PRIMARY_ROOT RESTORED_WORK NEW_WORK` independently
  checks the primary archive/manifest/files, all protocol pins, selection,
  response hashes/cursors, recovered bodies, budgets and public redaction using
  only the standard library.

Five focused evidence tests reject partial tar members, changed response bytes,
wrong cursors, future-height pages and complete/closed source selection. All five
existing lease/lock/cooldown guard tests also pass. The independent verifier
checks all 97 pins, 177 reused bodies, 332 reconstructed bodies and 19 raw tails.
See [validation.json](validation.json). Preparation made **zero provider requests,
zero model fits and zero new feature vectors**.
