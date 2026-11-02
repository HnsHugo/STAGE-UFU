# Final pre-cutoff network continuation — 2 November 2026

The original-route availability check returned HTTP200 for the first remaining source at 14:54:03 UTC. The earlier blocked-environment diagnosis was based on advertised flags rather than an observed provider refusal; this successful check supersedes it. No provider, route, proxy, account, IP or TLS change was made by the collector. The same successful counter check was referenced without another counter GET during this recovery run.

The first prepared pass was interrupted by execution control after two reference-request starts, with no saved response or final source result. Its consumed markers and zero-result export remain preserved under `../reference_tail_continuation_20261102_1455/`. A read-only check established that the actual validated collector had no eight-batch default: the frozen selection contains exactly 19 sources, one batch. This distinct successor pins that interrupted pass and the entire earlier lineage: 87 input fingerprints verified before execution. No denied or consumed marker was reused inside its original pass.

## Results

| Measure | Verified result |
| --- | ---: |
| Selected / finalized sources | 19 / 19 |
| New complete prior prefixes | 2 |
| New bounded-incomplete prefixes | 17 |
| New request records / successful responses | 332 / 332 |
| Remaining continuation network sources | 0 |
| Preserved predecessor predictor vectors | 1,376 |
| Current case / comparison vectors | 500 / 878 |
| Total predictor vectors | 1,378 |
| Comparison prefixes still bounded-incomplete | 122 |
| Full-current-history comparisons complete / incomplete | 864 / 136 |

The two exhausted prefixes are `comparison_0883` (14 pages, including the terminal empty page) and `comparison_0977` (eight pages, including the terminal empty page). Every other new prefix reached the frozen 16-page bound and supplies no predictor vector. These are confirmed transactions strictly below each unchanged reference cutoff. A complete prior prefix is not a verified complete current history or a cryptographic inclusion proof.

## Verification and preservation

All 19 private raw tails were re-extracted and all 332 saved responses checked by fingerprint. Both new fourteen-variable vectors were independently recomputed. Every existing vector, case row, unknown label, strict cutoff, source membership and full-history status was preserved. The composed schema-v2 view has exactly 1,500 distinct selected address hashes and the unchanged fourteen-column allowlist. Five reference-tail regressions pass. There was no training, split, paid retrieval or main-branch merge.

The private responses from the earlier 1 November pass were unavailable in this runtime; their old request manifests and audits remain pinned. Fourteen earlier successful response records for unfinished sources lacked local bytes and could not be reused. All new attempts are recorded in distinct successors. This run does not claim a fresh raw-response audit of the unavailable older caches.

Only redacted checkpoints, normalized prior-block evidence, request fingerprints, aggregate audits and this completion record are public. The two new work directories, private plans, responses and the sole counter response are preserved in a private backup with SHA-256 `052c7a4215f7cc7136ea05dffcb764e40f15b7e2fd838933689e4ccbaed61249` (73387033 bytes); its contents and access identifiers are excluded from GitHub.

Offline reproduction requires that private backup and a separate copy of the committed export, so the auditor does not overwrite historical files. Use the pinned `audit_reference_tail_successor.py`, protocol and baseline schema-v2 view. The exact completion/exclusion lists and dependency hashes are in `resume_checkpoint.json`. No network ID remains for this continuation; do not repeat the 122 bounded-incomplete prefix outcomes automatically.
