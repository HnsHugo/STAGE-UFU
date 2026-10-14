# FSF external donation comparison

The fixed 19-feature model scores the Free Software Foundation donation address `1PC9aZC4hNX2rmmrt7uHTfYAS3hRbph4UN` at **0.020963927926037452**, below the unchanged **0.15** threshold. No external label, score or test result is used to adjust fitting or threshold selection.

## History and audit

The complete confirmed history contains 2,593 transactions, including two coinbase receipts. Pagination is exhausted, provider counters are stable, and observed transaction counts, funded/spent output counts and funded/spent sums reconcile exactly. This is provider-counter reconciliation, not independent cryptographic inclusion verification.

| Counter | Observed value |
| --- | ---: |
| Transactions | 2593 |
| Funded outputs | 2469 |
| Spent outputs | 2465 |
| Received satoshis | 113022243778 |
| Spent satoshis | 112622218274 |

The raw compressed history is supplied separately as `fsf_history_20261014.json.gz`; SHA256: `133144439843f6407c4e797b79db4c12205bbcb3c6fd510c2ca778e9aa64eae9`. Its collection time and source record are retained in the score JSON. Large raw history bytes are excluded from Git. To recollect, run `collect_pilot_histories.py fsf_selection_20261014.json <new-directory> --max-pages 110` from the theft_cases directory. Later collection may yield different histories and scores.

The FSF official donation-purpose reference is https://www.fsf.org/about/ways-to-donate. It supports a comparison usage, not certification that every received payment is benign. The earlier evidence review documents address selection; it was not selected by its score. Exact-address overlap with both complete Real-CATS tables is checked by the scorer. Entity/counterparty independence remains unverified.

## Interpretation

There are now two donation-purpose comparison organizations: EFF (0.045173, no flag) and FSF (0.020964, no flag). The pilot still cannot estimate a reliable false-positive rate or generalization performance. The FSF activity lifetime is about 15.43 years and exceeds the training feature maximum; no features are missing. The score is not a calibrated theft probability.

See COINBASE_SUPPORT.md for the extraction correction and regression checks. Coinbase counterparty conventions have not been independently reconciled to a matching Real-CATS mining-related reference.
