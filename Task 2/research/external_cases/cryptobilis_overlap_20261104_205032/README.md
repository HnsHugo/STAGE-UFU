# CryptoBilis / Coldcard overlap and frozen-model eligibility

Completed 4 November 2026 UTC. This offline unit audits the fixed external source sample before model inference. It studies the proxy `cryptobilis_reference_source_membership`; it does not create verified theft, ownership or signing-device labels. No provider request, fitting, score, new partition, replacement or automation was performed.

## Result

| External class | Selected | Complete vectors | Complete vectors quarantined | Bounded incomplete, no vector | Eligible |
| --- | ---: | ---: | ---: | ---: | ---: |
| Graph-linked case source | 122 | 122 | 0 | 0 | 122 |
| Unattributed same-block comparison | 244 | 207 | 54 | 37 | 153 |
| Total | 366 | 329 | 54 | 37 | 275 |

The prespecified minimum of 20 eligible cases and 20 eligible comparisons passes on the combined external cohort. Eligibility is conditional on complete-case selection and measured-link quarantine. The 54 complete comparison vectors are retained intact in the acquisition view but excluded from the primary evaluation manifest. The 37 bounded prefixes remain null and unavailable. No record is replaced or recollected.

| Reference block | Selected cases | Eligible cases | Selected comparisons | Eligible comparisons | Quarantined complete comparisons | Bounded comparisons |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 970590 | 111 | 111 | 222 | 135 | 51 | 36 |
| 970591 | 11 | 11 | 22 | 18 | 3 | 1 |

The support gate is overall, as frozen in the transfer contract; it does not establish a minimum of 20 in each block. Case prevalence changes from 122/366 (33.33%) in the selection, to 122/329 (37.08%) among available vectors, then 122/275 (44.36%) after quarantine. Report this attrition explicitly in a later evaluation; the eligible sample is not an unbiased estimate of every selected source.

## Measured overlap and quarantine

All 1,866 selected identities enter the graph, including unavailable sources. Every available normalized prefix is checked: all 1,378 Coldcard vectors and all 329 CryptoBilis vectors reproduce from the saved normalized transactions, with 35,323 and 8,261 prior address/transaction observations respectively. Every transaction remains strictly below its source's frozen reference block.

| Cross-dataset criterion | Shared identifier/vector groups |
| --- | ---: |
| Exact address SHA256 | 0 |
| Shared prior transaction SHA256 | 45 |
| Shared reference-payment SHA256 | 0 |
| Identical complete fourteen-variable vector, including missingness | 1 |
| Transaction SHA256 across prior/reference roles, conservative additional guard | 45 |

These groups are overlapping criteria, not additive counts or independent observations. Vector equality uses exact rational numeric equality, preserving large integers and missingness, rather than float32-rounded inputs. Transaction-role unification was fixed before overlap computation; it guards a reference in one dataset appearing as a prior transaction in the other.

Four measured components span development and external data, containing 334 development identities and 67 external comparisons. Of those external comparisons, 54 have vectors and 13 are already bounded-incomplete. All external members of these components are quarantined; an incomplete member can propagate a known address/reference connection, but never supplies a fabricated prefix or vector. The remaining 24 bounded comparisons are also unavailable. A shared funding transaction or identical feature profile is a dependence guard, not proof of common ownership.

The full graph has 1,281 components. Union-find and an independent bipartite traversal agree. A second standalone verifier builds its own exact tuple-vector keys, transaction index and adjacency traversal directly from the pinned evidence; it reproduces every component and independently classifies all 366 external sources. The original 918 available-vector Coldcard components also reproduce exactly. The existing Coldcard partitions and model remain byte-unchanged; no development row is removed from its historical fit or reassigned.

## Evidence and interpretation limits

The audit exhaustively checks the available normalized prefixes and selected identities. It does not know missing prior links for the 122 bounded Coldcard prefixes or 37 bounded CryptoBilis prefixes, and does not establish entity independence. None of those 159 unknown prefixes is treated as evidence of no connection. This is one previously inspected external incident, not an untouched or prospective test. Source-level compromise, signing device and seed-origin labels remain unknown.

Individual CryptoBilis full-current histories remain `not_collected_for_this_source`. Coldcard's 864 complete / 136 incomplete comparison full-history statuses remain separate and unchanged. This audit reconciles no new current-history counter and never promotes prefix completion to full-history completion.

The frozen fourteen features, fourteen fixed missing indicators, Coldcard-training medians, exported tree and `>= 0.5` threshold are unchanged. Eligibility does not itself produce a score or a new F1. A later separately pinned inference unit may apply that same model to exactly the 275 eligible rows, with the fixed prevalence/inactivity/balance comparators and explicit attrition. Keep the 54 quarantined complete vectors and all 37 unavailable prefixes outside primary scoring. No tuning, refit, calibration, seed reroll or sample replacement is justified by this audit.

## Files and reproduction

- [Protocol and input fingerprints](protocol.json): 143 pinned input entries and fixed graph/quarantine rules.
- [Summary](summary.json), [component/link evidence](overlap_evidence.json.gz), and [per-source eligibility](eligibility_manifest.json.gz).
- [Primary reconstruction verification](verification.json), [standalone independent verification](independent_verification.json), and [execution checks](execution_validation.json).
- [Next-unit checkpoint](resume_checkpoint.json): acquisition remains closed; automations remain disabled.
- [Acquisition closure](../cryptobilis_reference_prefix_20261104_201345/README.md) and [original transfer contract](../cryptobilis_source_readiness_20261102/transfer_protocol.json).

The first schema preflight stopped before graph computation because the historical development target declaration includes an explanatory semicolon suffix. Only that parser compatibility was corrected. [The original preflight protocol](protocol_preflight.json) and [original code preflight commit](https://github.com/HnsHugo/STAGE-UFU/commit/08378e83dcb5b0eb110a7e7142c9dd171b7d2a23) are preserved; all overlap/quarantine rules remained unchanged.

Run from the repository root; no private raw-cache restoration or provider access is required for this normalized-evidence audit:

```sh
python "Task 2/research/external_cases/audit_cryptobilis_overlap.py" verify "Task 2/research/external_cases/cryptobilis_overlap_20261104_205032/protocol.json"
python "Task 2/research/external_cases/verify_cryptobilis_overlap_independently.py" verify "Task 2/research/external_cases/cryptobilis_overlap_20261104_205032/protocol.json"
python -m unittest discover -s "Task 2/research/external_cases" -p "test_cryptobilis_overlap.py"
python -m unittest discover -s "Task 2/research/coldcard" -p "test_source_comparison_feasibility.py"
```
