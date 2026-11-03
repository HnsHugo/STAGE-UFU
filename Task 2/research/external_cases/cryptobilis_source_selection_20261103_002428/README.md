# CryptoBilis source census and fixed comparisons

Executed 3 November 2026 UTC (2 November in São Paulo). One normal Blockstream source-counter GET and two original historical Blockchain.info rawblock GETs returned HTTP200, under the verified published lease and held local/global locks. Default verified TLS, original routes, no internal retries. The lease was released after the run; no automation was created or enabled.

The two complete height/hash/time-anchored blocks contain 7,944 transactions. Their 16,073 positive decoded input observations identify 9,356 unique sources; no input address is unresolved. All 122 saved CryptoBilis source references reconcile their exact input counts/values against this separate block representation.

| Block | Transactions | Eligible comparison sources | Fixed comparisons |
| --- | ---: | ---: | ---: |
| 970590 | 4,032 | 4,269 | 222 |
| 970591 | 3,912 | 4,934 | 22 |

The frozen 1,632 address-hash exclusions, original salt and first-reference rule yield all 244 planned comparisons with zero shortfall. No balance, age, fee, score or collection-success filter/replacement was used. An independent occurrence-minimum recount and ranked selection match every selected source/reference. The redacted input census reproduces the selected sample without publishing raw blocks or the decoded private execution plan.

The resulting selection has 122 graph-candidate sources and 244 same-block unattributed comparisons, all in the same external incident. Verified compromise/device and owner-report labels remain unknown. No source predictor vector or score was computed in this census unit; the Coldcard model is unchanged. A complete source prefix remains different from a full-current-history counter audit or a cryptographic inclusion proof.

See [protocol](protocol.json), [selection audit](selection_audit.json), [independent validation](execution_validation.json), [frozen transfer contract](../cryptobilis_source_readiness_20261102/transfer_protocol.json) and [selector](../select_cryptobilis_sources.py). input_census.json.gz and source_selection.json.gz are hashed public evidence; full blocks and raw addresses remain excluded. network_manifest.json.gz and run_stop.json retain the three consumed requests. The next unit is a separately pinned five-batch prefix pass over the fixed selection, preserving every outcome and the original fourteen definitions/cutoffs.
