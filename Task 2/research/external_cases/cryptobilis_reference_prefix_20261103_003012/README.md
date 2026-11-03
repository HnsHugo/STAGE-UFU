# CryptoBilis bounded prior-prefix acquisition

Executed 3 November 2026 UTC (2 November in São Paulo), after the anchored block census and fixed 366-source selection. This is one five-batch unit, not completion of the entire external acquisition.

## Actual coverage

| Class | Fixed total | Attempted in this pass | Complete prior-prefix vectors | Bounded incomplete | Still unattempted |
| --- | ---: | ---: | ---: | ---: | ---: |
| Graph-linked source candidates | 122 | 34 | 34 | 0 | 88 |
| Same-block unattributed comparisons | 244 | 66 | 56 | 10 | 178 |
| Total | 366 | 100 | 90 | 10 | 266 |

The workload order was frozen before features/scores: block height, then round-robin one source-ID-sorted case and two source-ID-sorted comparisons. This unit reaches only the first reference-block stratum; the remainder of both fixed strata stays in the original execution order. No failed/bounded source is replaced or reselected. All unknown compromise/device/owner-report labels and the fourteen strict prior-block definitions remain unchanged.

## Acquisition and verification

The published lease and global/historical local locks were checked before provider traffic. Exactly one ordinary counter GET on the first selected source preceded the bounded original Blockstream-route collector: two workers, at most one global request start per second, sixteen pages per source, fifteen-second timeout, no internal retry. All 574 new network responses returned HTTP200. Thirty-four reference transactions were reused offline from fingerprint-pinned, counter-reconciled original-provider collector snapshots and exact block/input evidence. The dispatch guard checks stop after the rate-limit wait; it cannot start queued requests after a refusal. No provider, route, account, proxy, IP or TLS workaround was used.

All five batch exports passed verification. The 100 raw tails re-extract exactly; all 90 complete vectors match an independent fourteen-variable recount. Every one of the 608 cached/new response fingerprints and each recorded cursor/endpoint sequence verifies. Five immutable batch snapshots and their delta verifications preserve progress at 20/40/60/80/100 sources. The ten non-exhausted prefixes have no vector. There were zero network errors or refused requests.

A validated exhausted prefix is provider-indexed history strictly below the frozen reference block. Reference confirmation, block/hash, own input count/value, funding closure, descending heights and terminal empty page verify. It is not reconciliation of a full current source history, a cryptographic inclusion proof or verified compromise/device identity. All individual full-history statuses remain separately not_collected_for_this_source.

## Saved evidence and continuation

[Coverage audit](coverage_audit.json), [execution checks](execution_validation.json), checkpoint.json.gz, request_manifest.json.gz and precutoff_feature_view.json.gz retain the normalized evidence, nulls and source identities. [Exact resumption](resume_checkpoint.json) lists all 266 network/unattempted IDs and excludes every one of the 90 completed and ten bounded-incomplete outcomes. It pins the protocol, current view/checkpoint/requests/stop and the selection/transfer/pilot/implementation lineage. Preserve every prior file and consumed marker. Prepare a distinct dated successor over at most the first 100 listed IDs, after global lease/lock/cooldown checks and one normal due counter GET. Fingerprint/endpoint/cursor-verified successful old pages may be reused offline; refused/consumed attempts must remain in their original pass.

The collector stopped and released its lease. No automation was enabled or created. Private plans, source addresses, full blocks and provider-response caches are excluded from GitHub; they are saved separately for exact restoration; see [private cache restoration metadata](private_cache_backup.json). The public repository contains only redacted evidence and recovery metadata.

The frozen Coldcard selection (1,500 rows), its 1,378 vectors and its model/protocol fingerprints are unchanged. CryptoBilis has no fitted model, split or score in this acquisition. Full cross-development overlap/quarantine and external feasibility remain pending completion of the fixed acquisition; no transfer F1, theft/device claim or independent-entity validation follows.

See the [frozen transfer contract](../cryptobilis_source_readiness_20261102/transfer_protocol.json), [selection](../cryptobilis_source_selection_20261103_002428/README.md), [pass protocol](../../cryptobilis_reference_prefix_20261103_003012_protocol.json) and [global policy](../../coldcard/comparison_access_retries_20261030/retry_policy.json).
