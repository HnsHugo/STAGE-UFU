# Coldcard source features before payment — 27 October 2026

## Executed unit and main result

This is an address-level **pre-payment** dataset pilot, continuing the
[source registry](../source_registry_20261027/README.md). It does not rank
collectors, train a model, assign hardware labels or alter historical experiments.

Eight addresses were fixed by SHA256 ranking with the prefix
`coldcard-prepayment-pilot-v1:42:` among the 500 candidate-day sources. No failed
or inconvenient address was replaced. Selection was fixed before collecting
their histories. All eight selected sources happen to spend one previous output
in their reference payment; this does not represent the 81 multi-input sources
in the full candidate cohort.

**All eight complete histories were collected and reconciled against stable
before/after provider counters.** Each contains two confirmed transactions:
one prior receipt and the reference payment. Fourteen features were computed
for every address after excluding the entire reference-payment block and all
later blocks. No collection failed and no history hit the four-page limit.

| Observation before the payment block | Actual result |
| --- | --- |
| Sources with computed features | 8 / 8 |
| Earlier transactions / receipts | Exactly 1 per source |
| Earlier spending transactions | 0 for every source |
| Unspent address outputs at cutoff | Exactly 1 per source |
| Address balance | 21,450,000–134,377,744 sat (0.2145–1.34377744 BTC) |
| Blocks since first/last activity | 22,671–268,153 blocks |
| Available historical spending-fee observations | 0 |
| Independent incident groups | 1 |
| Verified compromise/hardware labels | 0 |

This establishes a reproducible prefix-feature pipeline and a concrete
description of this small sample: previously funded addresses with no earlier
spending. It does not establish hardware control, wallet-wide dormancy, theft or
a general distinction from other Bitcoin addresses. The address history is not
the complete entity/wallet history.

## Temporal boundary and evidence

The cutoff is the reference payment's **block height**, and inclusion is strictly
`history_height < payment_height`. Same-block activity is omitted, even if it
could precede the payment. Bitcoin header timestamps can be nonmonotone and do
not provide intra-block ordering; a timestamp-only filter is not used.

The cutoff height, payment identifier and incident group are metadata, not
predictors. The sample is selected retrospectively from a known case: feature
filtering does not turn it into prospective detection. The histories were
retrieved now, not archived before the incident; no historical API-availability
claim follows. No train/validation/test split or performance metric is produced.

The extractor rebuilds prefix UTXOs from earlier receipts minus earlier consumed
outpoints. It never reads a provider's current `spent` flag as a historical
feature. Prior spent outputs must match earlier recorded receipts. The known
payment, its fees and all later transactions are excluded from predictors.

The payment under investigation cannot by itself establish the prior owner's
fee-setting policy or the signing device. In this sample, there is no earlier
outgoing fee history at all. Incoming transaction fees are not substituted for
the recipient's own spending history.

## Feature definitions

| Fields | Unit / definition | Empty-prefix or missing policy |
| --- | --- | --- |
| `confirmed_tx_count`, `receipt_tx_count`, `spending_tx_count` | Transactions in earlier blocks; a self-payment may count as receipt and spending | Zero only for a complete empty prefix |
| `received_output_count`, `spent_output_count`, `unspent_output_count` | Matching source-address outpoints, reconciled by identifier and value | Zero only for complete data |
| `received_sat`, `spent_sat`, `balance_sat` | Integer satoshis; balance = earlier received minus earlier consumed | Zero only for complete data |
| `active_block_count`, `activity_span_blocks` | Distinct earlier block heights; latest minus earliest height | Span null if no earlier activity |
| `blocks_since_first_activity`, `blocks_since_last_activity` | Cutoff height minus first/last earlier activity height | Null if no earlier activity; not elapsed calendar time |
| `median_spending_tx_fee_rate_sat_vb` | Median fee / ceil(weight/4) for earlier transactions spending source outputs | Null without earlier spending; not a proven device/owner policy |

Incomplete/unstable histories produce **no feature vector**, rather than false
zeros. Compromise and hardware labels remain null. All rows retain
`coldcard_2026` as the split group and must not be treated as eight independent
incidents or scattered into a supposedly independent train/test split.

The [summary](summary.json) reports **nine constant columns**, one entirely
missing fee column and two pairs of duplicate varying columns: received amount
equals balance, while first/last activity ages coincide. Thus fourteen extracted
columns do not mean fourteen independent, informative signals. More diverse
histories are needed before model comparison is worthwhile.

## Saved files and provenance

- [Protocol](../prepayment_protocol_20261027.json): pinned registry inputs,
  selection, cutoff and bounded collection settings (two workers, four pages,
  eight-second request timeout, no replacement).
- [Collection manifest](collection_manifest.json): selection fingerprint, source
  reference hashes, individual snapshot SHA256/bytes, collection dates and audits.
- [Prefix evidence](prefix_evidence.json): only earlier-block normalized
  transactions, amounts and hashed transaction/outpoint references.
- [Feature rows](features.json): fourteen predictors per eligible source,
  separated from group/cutoff metadata and unknown labels.
- [Aggregate summary](summary.json): real coverage, feature ranges, missingness,
  constant/duplicate columns and limitations.
- `raw/` (generated locally, ignored by Git): eight exact compressed provider
  histories. The manifest pins their original bytes. A new public collection is
  a new snapshot and need not reproduce those bytes or collection timestamps.

The provider is `https://blockstream.info/api`. Address identities can be
reconstructed from the pinned source registry and deterministic selection.
Hashed references are used to avoid publishing another full address/history
list; they do not guarantee anonymity. Counter and outpoint consistency is not
cryptographic block-inclusion verification or hardware attribution.

## Reproduce and verify

From the repository root, the **published prefix evidence** is sufficient for an
offline check without the separately retained raw histories:

```bash
python "Task 2/research/coldcard/prepayment_pilot.py" verify \
  "Task 2/research/coldcard/prepayment_protocol_20261027.json" \
  "Task 2/research/coldcard/prepayment_pilot_20261027"
```

With the original raw snapshots, `reproduce` re-extracts and compares every
analysis byte. To perform a new bounded collection, choose a new directory:

```bash
python "Task 2/research/coldcard/prepayment_pilot.py" collect \
  "Task 2/research/coldcard/prepayment_protocol_20261027.json" \
  "Task 2/research/coldcard/prepayment_pilot_new_snapshot"
python "Task 2/research/coldcard/prepayment_pilot.py" analyze \
  "Task 2/research/coldcard/prepayment_protocol_20261027.json" \
  "Task 2/research/coldcard/prepayment_pilot_new_snapshot"
python -m unittest discover -s "Task 2/research/coldcard" -p 'test*.py'
```

Nine new tests cover future/same-block exclusion, nonmonotone times, future
spent flags, fee units, historical UTXOs, duplicate references, empty prefixes,
ordering and incomplete-history handling. The
[execution record](../../../verification/prepayment_pilot_20261027.json)
records the actual checks and raw/offline reproductions.

## One next aligned unit

Extend this fixed extractor to a small, prespecified deterministic subset of the
**81 multi-input candidate sources**, with an explicit pagination budget and no
replacement after failures. This checks a source-history shape absent from the
eight-address pilot before considering a wider dataset or a classifier.
