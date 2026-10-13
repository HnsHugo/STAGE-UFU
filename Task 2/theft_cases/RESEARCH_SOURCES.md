# Additional sourced candidate addresses — 13 October 2026

## New sources and verified downloads

Original source files were downloaded at pinned commits, hashed, parsed and checked for duplicate addresses. research_download_manifest.json records URLs, commit IDs, byte counts and SHA-256 hashes. research_source_audit.json records actual row counts, columns and category counts. No model is trained in this step.

| Source | Actual candidate coverage | Interpretation |
| --- | --- | --- |
| somaxbt/coldcard-drain-addresses | 597 unique addresses | Source-asserted collector/holding/park/vault/consolidation roles; reconstruction has stated attribution limits |
| somaxbt/btcpay-lnd-drain-2026-08 | 2 unique collectors | Research attribution supported by described victim testimony, not our independent verification |
| sjdseu/Real-CATS, CB.tsv | 711 active Hack and 600 active Theft addresses | Dataset category assertions; per-address roles/cases still require provenance review |
| sjdseu/Real-CATS, BB.tsv | 86,583 active benign-labeled addresses | Potential comparison pool; label is a dataset assertion rather than a guarantee of every transaction's legitimacy |

Source repositories:
- https://github.com/somaxbt/coldcard-drain-addresses
- https://github.com/somaxbt/btcpay-lnd-drain-2026-08
- https://github.com/sjdseu/Real-CATS

Coldcard roles count 6 collectors, 4 holding addresses, 293 parks, 293 vaults and 1 consolidation. Victim lists were not imported. All waves remain in a conservative shared split group; a new source for the same incident is not a new independent theft case.

BTCPay's report describes two collection addresses and victim corroboration. Exact role evidence and relation to the reported exploit still need independent review. Original source balance/purity fields are dated observations, not decision-time predictive features.

Real-CATS files contain 90,164 BB rows and 90,597 CB rows in total, including zero-transaction addresses. Their active counts match the published 86,583 and 40,032. BB and CB share no address, and neither file has duplicate addresses. The downloaded criminal table contains multiple abuse categories; only active Hack/Theft categories are selected here. Other categories are not renamed theft.

## Candidate registry

research_candidates_20261013.json contains 1,960 source assertions: 597 Coldcard roles, 2 BTCPay collectors, 1,311 active Real-CATS Hack/Theft addresses, and 50 deterministic benign comparison candidates. The 50 are selected by SHA256(address) among active benign rows, independent of financial features. This is a feasibility pilot, not a representative sample.

Every record retains a pending-review training label. Real-CATS case IDs, roles and label-availability dates are missing in the inspected tables and remain null/unknown. The registry is not ready for case-disjoint supervised training. Duplicate or overlapping assertions across sources must be reconciled rather than treated as independent examples.

## Schema and reuse limits

Real-CATS has 36 table columns including address, label, transaction IDs and checks. Financial column names do not by themselves establish units: observed total_received_BTC values include integer-like amounts that require schema confirmation. Some source features summarize complete histories. They are not automatically compatible with the cutoff-safe feature schema or Elliptic++.

Real-CATS includes an MIT license in the inspected commit. The two research repositories contained no explicit LICENSE file in the inspected trees. Raw TSV/CSV files and victim lists are not republished here; source URLs, hashes and factual candidate assertions support review and reproducible local retrieval.

## Reproduction and next steps

Download the exact URLs listed in research_download_manifest.json into a directory preserving `<repository-name>/<source-path>`, then place the manifest at its root:

```bash
python import_research_sources.py /path/to/source_directory new_candidate_registry.json
```

The importer verifies source hashes before creating a new registry. Next: investigate per-address provenance and roles, confirm monetary units, check source overlaps with existing case references, collect compatible historical windows for a small reviewed subset, and define a negative-comparison policy and case-level split before fitting. An absent report is never converted into a legitimate label.
