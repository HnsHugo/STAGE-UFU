# Six-address historical collection pilot

## Selection and scope

The pilot selection is fixed in pilot_selection_20261013.json: both published BTCPay collectors, one Real-CATS Hack address, one Theft address and two benign addresses. Real-CATS candidates must have 1–10 source-reported transactions and are then ordered by SHA256(address), without financial feature selection. This is a feasibility sample, not a representative dataset.

All source categories remain assertions pending evidence review. Real-CATS case IDs, address roles and label availability dates are unknown. The two collectors share a single BTCPay case group. There is no valid supervised case-disjoint evaluation yet.

## Collection and feature checks

Six complete confirmed histories were retrieved using at most six pages per address and two workers. Pagination exhaustion, stable provider counters, distinct TXIDs and reconstructed funded/spent amounts agree for all six. This is provider consistency, not independent inclusion verification or a guaranteed atomic snapshot.

For every address, cutoff is 24 hours after its first observed confirmed receipt, with a seven-day lookback. Only earlier transactions enter features. No current spending status or future transaction enters the snapshot. Address creation/maturity is standardized retrospectively, but calendar periods and source-label applicability still differ.

Git contains normalized transaction observations: script bodies are omitted, while values, addresses, input outpoint references, fees, weights and confirmation status are retained. Original retrieval hashes are retained separately. Stored normalized histories were checked to reproduce every snapshot exactly. The manifest records current file hashes and source selection provenance. Regeneration uses live provider data and may legitimately include new later transactions while historical cutoffs remain fixed.

## Descriptive snapshots

| Source assertion | Transactions before cutoff in window | Received sat | Spent input sat | Interpretation |
| --- | ---: | ---: | ---: | --- |
| BTCPay collector A | 71 | 174760889 | 0 | Multiple receipts, no early spending |
| BTCPay collector B | 1 | 46608022 | 0 | One receipt, no early spending |
| Real-CATS Hack | 2 | 1048562282 | 0 | Two early receipts |
| Real-CATS Theft | 2 | 4902803 | 4902803 | Receipt and early spending |
| Real-CATS benign sample 1 | 1 | 106855 | 0 | Receipt, no early spending |
| Real-CATS benign sample 2 | 2 | 11704280 | 11704280 | Receipt and early spending |

These observations do not establish a general rule. Early spending appears in both the Theft and benign categories; accumulation without early spending appears in both attributed and benign examples. Own input value spent is not identical to payment value to another owner because change and self-transfers require interpretation.

Whole-transaction outgoing fee-rate summaries are null when no outgoing transaction is observed. Incoming fees are not used as a recipient policy. These features are not a verified mapping to the Elliptic++ model's features; no forest scores are reported.

## Reproduction

```bash
python collect_pilot_histories.py pilot_selection_20261013.json new_pilot_history_directory
python -m unittest discover -p 'test_*.py' -v
```

The output directory must be new. A partial/error result keeps the manifest incomplete; snapshots are emitted only for provider-count-complete histories. Six theft-case tests pass. Saved file checksums and snapshot reproduction were also checked on the real pilot.

## Next priority

Investigate source provenance and incident roles for the selected Real-CATS references; expand reviewed cases and comparison groups before assigning training labels. Harmonize calendar periods as well as observation maturity, and preserve case/entity relationships. A six-address demonstration cannot provide reliable model performance.
