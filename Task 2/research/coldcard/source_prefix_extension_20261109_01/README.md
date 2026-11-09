# New coverage extension beyond the exhausted 16-page prefixes

Prepared 9 November 2026 after Hugo authorized beginning the supervision update.
This is a new coverage scope, not a restart of a refused or exhausted old pass.
The old 122 Coldcard and 37 CryptoBilis bounded outcomes remain preserved.

## Offline work actually completed

- All three required CryptoBilis private archives were located, downloaded and
  verified against their declared sizes/SHA256 values. They were restored as
  separate immutable layers, preserving archive-level metadata collisions.
  Old collector lock/lease-ready flags were not restored.
- The existing Coldcard private work folders were reused without overwriting
  their results, failed markers or temporary partial files.
- Private plans are available for all 159 bounded-prefix targets. Saved
  16-page anchored tails are usable for 29 Coldcard and 37 CryptoBilis sources.
  Every reused response fingerprint and endpoint/cursor sequence is checked.
- All 87 published predecessor input pins were verified. The new protocol pins
  their deduplicated lineage plus the latest checkpoint, stop, request manifest,
  predictor view, pilot gate and actual original collector/transport code.

## First bounded extension

Select the first 20 lexically ordered still-unavailable Coldcard IDs from the
latest fixed view. They all have verified reference responses and 16 saved tail
pages: 340 saved responses are reused offline. Keep the same source IDs,
reference anchors, 14 definitions, unknown labels and full-history statuses.
No complete prefix is selected, no address is replaced and no old failed marker
is copied. The old stopped scopes remain immutable.

Extend each selected source to at most 32 total tail pages, including any empty
terminal page. The maximum new tail-page budget is 320, plus one ordinary
availability counter, at most 20 fresh reference-status checks and at most 32
funding-status checks. This is a bounded first extension, not an estimate that
the entire 159-source coverage problem will be solved within that budget.

Use the existing validated collect_reference_tail.py and
collect_reference_tail_many.py, with the eight-control exact-match gate,
two workers, one global request start per second and timeout 15s. The wrapper
adds a stop check before a new source starts and verifies the live published
lease permit before creating the unchanged original-route HTTP client.
Historical/local locks and an idle due predecessor state are required before
the new running lease is published. Five guard tests prove that missing,
foreign or expired leases, a future cooldown or a held historical lock enter
no HTTP client.

Before provider traffic, the process holds all declared historical locks and
the new local work lock; the controller must publish and read back the new
running lease/protocol on GitHub, then write the verified private permit.
The first request is exactly one ordinary counter GET for the first selected
address, through the original Blockstream route, inherited proxy and default
verified TLS. A 200 allows collection. The first 403/429 stops new starts;
there is no internal retry or provider/account/proxy/IP/TLS fallback. Retain
Retry-After and apply the recorded cooldown/backoff policy, uncapped for a
longer server delay. A 403 pauses collection and keeps automation disabled.

Complete vectors require exhausted anchored prefixes, funding closure,
height/hash/input count/value checks, ordered unique transactions and an empty
terminal page. Prefix completion never promotes full-current-history coverage.
Further collection of still-bounded sources needs its own larger resumable
scope; do not rerun this stopped scope or repeat its consumed markers.

## Public and private boundaries

The protocol, IDs, response fingerprints, numerical budgets and normalized
exports are public. Raw plans, addresses, provider bodies and lock paths stay
in private work/archives. The new saved-response reuse manifest contains only
source IDs, stage names, predecessor pass names and fingerprints. No automation
is created or re-enabled. Run receipts distinguish new HTTP responses from
offline reuse; a prepared plan is not a completed collection.
