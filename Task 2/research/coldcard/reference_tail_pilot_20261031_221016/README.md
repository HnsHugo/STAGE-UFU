# Anchored pre-cutoff history pilot

Eight previously full-counter-verified comparison histories cover all four frozen reference blocks and prior counts from zero to 348. Every recovered normalized prior-block transaction and all fourteen predictors match exactly. The normal source-counter access check returned 200; 79 original-route requests completed without errors. Five new temporal/cursor tests and three page-ledger tests pass.

The provider API documents newest-first confirmed cursor history. Its indexed implementation can seek to a confirmed payment, avoiding newer transactions. Reference transaction identity, block/hash, input count/value, funding closure, height ordering and an empty terminal page are checked. Reorgs, absent funding, duplicate transactions and non-exhausted tails do not yield predictors. See [validation](pilot_validation.json), [expected normalized controls](expected_control_evidence.json.gz) and [source assessment](provider_contract_sources.json).

This validates the provider-indexed pre-cutoff scope on the eight controls. It is not an independent audit of the hosted index, cryptographic inclusion proof or full-current-history counter reconciliation. The original 1,500-row view and its full-history statuses stay unchanged. Unknown labels are preserved. No model/split. Raw addresses, TXIDs and page bytes remain private.
