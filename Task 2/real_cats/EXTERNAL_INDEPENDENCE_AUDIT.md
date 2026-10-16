# External pilot independence audit

Executed at `2026-10-15T18:12:47.665207+00:00` on 11 saved pilot histories: 2,883 distinct confirmed transactions, 5 conservative evidence groups. All history hashes, focal identities, source records and five provider counters reconcile. Both full Real-CATS source hashes match the score reports. No model was fitted, tuned or used for prediction.

**0 focal addresses occur in the source tables; 1 pilot histories share 2 source-extremum transaction IDs with 2 training addresses.** Exact-address disjointness does not establish transaction independence. Transaction overlaps neither establish common ownership nor transfer source labels to the pilot. The fixed scores and threshold remain unchanged.

## Saved descriptive scores by evidence group

| Evidence group | Addresses | Above 0.15 | Minimum | Median | Maximum |
|---|---:|---:|---:|---:|---:|
| binance_2019 | 1 | 1 | 0.275116 | 0.275116 | 0.275116 |
| btcpay_lnd_20260807 | 2 | 2 | 0.210626 | 0.241282 | 0.271938 |
| eff | 1 | 0 | 0.045173 | 0.045173 | 0.045173 |
| fbi_tradertraitor_2023_08_22_multiple_heists | 6 | 3 | 0.118753 | 0.186596 | 0.236503 |
| fsf | 1 | 0 | 0.020964 | 0.020964 | 0.020964 |

These are previously saved source-category scores and descriptive alert counts, not group accuracy or estimated detection performance. Group identifiers are retained from the saved attribution records; multiple addresses from one group do not become independent incidents.

## Source coverage and provenance

| Source table | All address rows | Rows with an extremum ID | Distinct extremum txids |
|---|---:|---:|---:|
| BB.tsv | 90,164 | 86,583 | 170,077 |
| CB.tsv | 90,597 | 40,028 | 108,200 |

The source tables are pinned by byte hashes:

- `BB.tsv`: `3bfe26f493e5767737c9ecf4c654009067c162dc7fa6fec68b0ab8234d4431e9`.
- `CB.tsv`: `faf3978f5c9ce3b1257af72ac01975d657ab7529f66faf1a66f1f22f99fbb1ec`.

Each of the four maximum/minimum sent/received transaction-ID columns was scanned for every source row, including rows excluded from the binary benchmark. These columns are only a subset of each source address's transactions. Zero extrema matches cannot prove full-history transaction disjointness.

The original deterministic identity split was reconstructed using address, source category and activity count only. No reserved-test predictions or predictive features were used. train: 52,736; validation: 17,579; reserved_test: 17,579. The JSON records source, score, history, script and split-code hashes, a logical membership hash and runtime versions. The source citations retained in history records were not newly authenticated by this offline audit.

## Observable source overlap

A co-address is another decoded address appearing in an input or output of any focal transaction. It can be a change address, another batched recipient, or an input participant. It is not automatically a direct counterparty, common owner or shared incident.

| Focal address | BB co-addresses | CB co-addresses | BB extrema tx matches | CB extrema tx matches |
|---|---:|---:|---:|---:|
| 3LTu6uavQ4A3kgDauZipyGqcHQEUSVe2so | 49 | 1 | 0 | 0 |
| 19jSfadPiKa4aCefj4F7uEYbhMEt2L8SCH | 0 | 0 | 0 | 0 |
| 17C7EZC1VTrXzSQneiaJv2W6tQh1vCRSnF | 0 | 0 | 0 | 0 |
| 3LU8wRu4ZnXP4UM8Yo6kkTiGHM9BubgyiG | 0 | 0 | 0 | 0 |
| 34VXKa5upLWVYMXmgid6bFM4BaQXHxSUoL | 0 | 0 | 0 | 0 |
| 3AAUBbKJorvNhEUFhKnep9YTwmZECxE4Nk | 0 | 0 | 0 | 0 |
| 3NbdrezMzAVVfXv5MTQJn4hWqKhYCTCJoB | 0 | 0 | 0 | 0 |
| 3PjNaSeP8GzLjGeu51JR19Q2Lu8W2Te9oc | 0 | 0 | 0 | 0 |
| 39idqitN9tYNmq3wYanwg3MitFB5TZCjWu | 0 | 0 | 0 | 0 |
| bc1q8m9h3atn4cqeqhu3ekswdqxchp3g7d4v3qv3wm | 0 | 2 | 0 | 2 |
| 1PC9aZC4hNX2rmmrt7uHTfYAS3hRbph4UN | 30 | 35 | 2 | 2 |

Each source match, source field, original split membership and observed input/output role is recorded in the JSON. Matches to source categories excluded from training are not training overlap. A transaction can match both tables; table counts must not be added to estimate unique transactions.

### Transaction overlaps with training

| Pilot address | Transaction ID | Training address | Tx outputs | Pilot received (sat) | Source received (sat) |
|---|---|---|---:|---:|---:|
| 1PC9aZC4hNX2rmmrt7uHTfYAS3hRbph4UN | c1f33d23fa3fec1e1902823b327cf5f1e92246ce1e77f44df2598e2ba03aa194 | 3Hc4UkbsGGh74VzBZ77UQ1fhSHapzdQNiT (BB.tsv) | 556 | 547 | 547 |
| 1PC9aZC4hNX2rmmrt7uHTfYAS3hRbph4UN | ee4a3120532cc18c2ad763c51f113aaf7fb25a7488b6b2d7896741a120b2dd89 | 38hKmVCwzmMUHNfXXT6bD6xrVhNWtNiurC (BB.tsv) | 2801 | 546 | 546 |

All listed overlaps are co-receipts: the pilot and training address both appear as recipients, and neither supplies an input to that transaction. This establishes shared transaction data but not a direct transfer between those addresses. The effect of these overlaps on scores is not measured by this audit.

## Relations within the pilot

All 55 address pairs were compared. 0 pairs share at least one transaction ID; 4 pairs share decoded co-addresses:

| Address A | Address B | Shared co-addresses | Same evidence group |
|---|---|---:|---|
| 3LTu6uavQ4A3kgDauZipyGqcHQEUSVe2so | 1PC9aZC4hNX2rmmrt7uHTfYAS3hRbph4UN | 8 | No |
| 19jSfadPiKa4aCefj4F7uEYbhMEt2L8SCH | 17C7EZC1VTrXzSQneiaJv2W6tQh1vCRSnF | 1 | Yes |
| 3PjNaSeP8GzLjGeu51JR19Q2Lu8W2Te9oc | 39idqitN9tYNmq3wYanwg3MitFB5TZCjWu | 1 | Yes |
| bc1q8m9h3atn4cqeqhu3ekswdqxchp3g7d4v3qv3wm | 1PC9aZC4hNX2rmmrt7uHTfYAS3hRbph4UN | 1 | No |

1 parent-output/child-input dependencies were verified across histories. Outpoint indices, values and decoded addresses agree. These links do not establish common private-key ownership; evidence groups were not merged.

- `7029f7ff0bdd859e075287d9b7fb61ba38ed63d7ba19dedae6c73047554998c0:1` is consumed by input 4 of `054f3a8e1bb6856017db024eb675091f458d9ecc82bfb45bcffa19013a631a80` (15,258 sat); parent history `17C7EZC1VTrXzSQneiaJv2W6tQh1vCRSnF`, child history `19jSfadPiKa4aCefj4F7uEYbhMEt2L8SCH`.

## Limits

- Matching file hashes establishes saved-byte identity, not source authenticity or blockchain inclusion.
- Provider counters reconcile all supplied saved histories; cryptographic inclusion is not verified.
- Source transaction identifiers cover four extrema only; missing matches cannot prove complete transaction disjointness.
- Decoded co-addresses include inputs, change and batched outputs; shared co-addresses do not establish shared ownership.
- Exact address disjointness is not transaction disjointness; overlapping transactions can be multi-recipient payments.
- Evidence groups are conservative attribution/comparison groups, not verified mutually independent entities or incidents.
- The FBI source groups several heists without mapping each address to an originating incident.
- Donation purpose does not certify every received coin as benign; source crime labels do not transfer through transaction links.
- Source tables lack complete incident/entity identifiers; full entity and incident independence remains unverified.
- Saved histories use individual collection dates and later activity; this audit does not evaluate detection at attribution time.
- Pilot scores were already inspected; these cases are a descriptive development/stress-test set, not a new untouched evaluation.
- No precision, recall, F1, false-positive rate, calibrated probability or population performance is estimated.

## Reproduction

From `Task 2/real_cats`, with the source checkout and saved raw artifacts available:

```bash
python audit_external_overlap.py /path/to/real-cats-source \
  --scores expanded_external_scores_20261014.json fsf_external_score_20261014.json \
  --history-root .. --history-root /path/to/raw-artifacts \
  --output external_independence_reproduced.json \
  --markdown EXTERNAL_INDEPENDENCE_REPRODUCED.md
python -m unittest test_external_overlap -v
```

The command refuses to overwrite existing reports. It requires the exact saved history bytes referenced by the input score reports; no new provider calls occur. Original source tables and pilot histories remain unchanged.
