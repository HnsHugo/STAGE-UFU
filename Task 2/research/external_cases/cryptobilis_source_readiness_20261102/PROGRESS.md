# CryptoBilis source readiness - recovery checkpoint

This checkpoint preserves the observed scope and design decisions after local workspace resets. It is not a completed source-history collection or transfer evaluation. The implementation draft was not committed before the reset; restore it, test it and publish the complete outputs before claiming readiness.

## Read-only observations already obtained

- Base: c4d22e0a2710581ff4e8fc35ae37c5afa5ff3073, branch task-2-wallet-analysis.
- Reused two collector histories pinned by central_protocol_20261020.json: SHA256 f4d3e1e703c40207b648f6ceacfc555586764b82d05406a998cb0a2ea728caa0 and ccd6c134cc3f0168fc436fe80deb355e04c71cf3dd580c8cdd7b4a316eee57c9.
- Fixed event scope: 9 October 2026 UTC, reference blocks 970590 and 970591.
- Observed event payments: 76 + 46 = 122. Unique decoded input source addresses: 122. Input outpoints: 140.
- Twelve payments have multiple inputs, none has multiple distinct input addresses, and all 122 have one output.
- Reference input values total 20,381,783,801 sat; fees total 2,963,800 sat. These are measured transaction values, not certified stolen totals or predictors.
- Seven outside-window payments involve one additional source address, with zero overlap with the 122 event sources.
- Zero exact source-address overlap with the 1,500 Coldcard development selections; 140 direct funding TXID hashes have zero matches against 34,640 completed Coldcard prior references. Full source-prefix overlap remains unknown.
- Existing historical role evidence identifies the two collector references. The Bitquery investigation could not be reopened via the web reader; no refreshed source contents or victim/device labels are claimed.

## Frozen direction for the pending implementation

Recover and publish only hashed source/reference/outpoint evidence from the existing pinned histories. Keep all compromise, device and owner-report labels unknown. Both collectors and any unresolved participant example belong to one CryptoBilis incident.

Prespecify a complete two-block input census and deterministic same-period comparisons, at 2:1 per first-reference block: 111 sources / 222 planned comparisons at 970590, and 11 / 22 at 970591. Actual selected comparisons remain zero. Exclude prior Coldcard development addresses and known case-adjacent sources/collectors before any external score is inspected.

The external target is cryptobilis_reference_source_membership, an explicitly different incident-specific graph proxy. Assess transport of the frozen Coldcard membership profile; never rename old known_coldcard_core_membership labels or report theft/device F1.

Use the unchanged fourteen strict prior-block definitions, exported Coldcard training medians and fixed missing indicators. Keep the existing model, >=0.5 threshold and all Coldcard splits unchanged. No fit, refit, calibration, parameter search or score-based selection. Keep the entire CryptoBilis incident outside fitting; retain/quarantine measured cross-development overlaps, report attrition without replacement.

## Actual remaining work

Restore the implementation, add failure-oriented tests, independently recount the source registry and publish a complete configuration, hashed registry, input evidence, readiness audit, transfer protocol and output fingerprints. No source vectors, control sample, external scores or new F1 exist yet.

Future provider acquisition needs its own pinned pass, lease/OS-lock/cooldown checks, original provider/route/verified TLS and the established refusal policy. Do not start a collector or automation in this readiness unit. Preserve all old results and private caches.
