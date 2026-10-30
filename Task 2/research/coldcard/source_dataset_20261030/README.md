# Consolidated Coldcard source-address dataset — 30 October 2026

## Requirement, scope and result

This executes the next unit in the [alignment review](../../../ALIGNMENT.md):
consolidate the existing source-address features and evidence, then characterize
actual source behaviour before choosing a comparison and predictive experiment.
No new network collection, fitting or train/test split took place.

The fixed population is **500 source addresses** whose reference payments entered
the known collector during 30 July 2026 UTC, in blocks 960188–960191. Five later
sources remain excluded. An address is not a person, wallet, device or independent
incident. The cohort was selected retrospectively from a known incident.

| Observation | Result | Meaning |
| --- | ---: | --- |
| Complete source feature vectors | 500 × 14 | Unchanged prior-block extractor |
| Externally corroborated case relations | 500 | Two pinned chain reconstructions, not independent victim/device verification |
| Owner-reported loss / Coldcard association | 1 / 1 | One account, exactly mapped to `cohort_0002` |
| Independently verified compromise / device labels | 0 / 0 | Unknown does not mean a negative label |
| Incident groups / documented controls | 1 / 0 | No independent-incident evaluation yet |
| Sources with exactly one prior transaction | 411 (82.2%) | A predominantly sparse history population |
| Sources without prior spending | 482 (96.4%) | Historical spending-fee feature is null for these sources |
| Sources with prior spending | 18 (3.6%) | Fee-rate distribution applies only to this subset |
| Prior address/transaction observations / distinct references | 1,445 / 1,431 | Shared transaction references are not ownership proof |
| Reference inputs / gross source-input value | 1,324 / 59,451,379,184 sat | Input value before reference-payment fees; not all incident losses |
| Reference payments consuming all known prior-block UTXOs | 499 (99.8%) | Address-level outcome, excluded from predictors |

**One partial reference spend:** `cohort_0435` had 225 known unspent outputs,
worth 50,165,157 sat, before its reference block. Its payment consumes 200 outputs,
worth 31,558,288 sat. The other 25 known outputs, worth **18,606,869 sat**, are not
consumed by that payment. This is not a claim about their eventual fate, a later
wallet balance, or the contents of an entire wallet. Every reference input across
the cohort matches a known prior-block unspent output with the same value.

## Files and provenance

- [Pinned protocol](protocol.json): observation unit, target, cutoff and hashes.
- [Consolidated view](view.json.gz): gzipped JSON with 500 address-level rows,
  predictor allowlist, input hashes and row-level evidence pointers.
- [Descriptive summary](summary.json): full feature profiles and outcome checks.
- [Builder](../consolidate_source_dataset.py) and [focused tests](../test_source_dataset.py).
- [Execution verification](../../../verification/source_dataset_20261030.json).

Inputs are the combined recovery checkpoint, its recovery protocol, the frozen
extractor, the registry protocol and reference history, the
[external comparison](../source_corroboration_20261030/README.md) and the
[first-person report layer](../owner_report_adjudication_20261030/README.md).
Their historical bytes and labels are unchanged. The comparison retains the
pinned SomaxBT and Alvaro P. source references and attribution; both analyze the
same chain. Owner rows retain report IDs, source permalinks, account hashes,
reported models, date uncertainty and caveats. Private caches and external raw
CSVs are not required to reproduce this join from the committed artifacts.

Source/payment hashes are stable join identifiers, not anonymization guarantees.
Exact addresses can already be reconstructed locally with the existing registry
protocol. This deliverable does not create a new bulk list of alleged victims.

## Row schema and predictor boundary

| Field | Content | Predictor use |
| --- | --- | --- |
| `source_id`, address/payment hashes, block metadata | Stable joins and cutoff audit | Excluded |
| `incident_group`, `verified_entity_group` | One incident; verified entities unknown | Excluded; retain for evaluation design |
| `features` | Exactly the existing fourteen features | Only allowed predictor fields |
| `history_evidence` | Collection date, raw/prefix hashes, provider completeness | Excluded |
| `case_evidence` | Corroborated retrospective source relation | Evidence/possible study target; excluded from predictors |
| `event_evidence` | Reference input counts, values and prior UTXO consumption | Outcome reconstruction; excluded |
| `owner_reports` | Exact sourced declarations, dates and caveats | Evidence only; excluded |
| `labels` | Reported loss/hardware versus independently verified targets | Targets/evidence only; excluded |
| `verified_target_training_eligible` | False for this snapshot | Administrative; excluded |

All features use only confirmed transactions at heights **strictly below** the
reference-payment block. The entire reference block and future are excluded.
Missing fee rates remain null, not zero or reference-payment fees. Label publication
and availability dates remain unknown where the source did not establish them;
event dates and collection dates do not substitute for those dates.

## Feature distribution

Amounts are integer satoshis; spans/ages are block differences, not calendar time.
The fee rate is sat/vB for prior transactions spending source outputs. It is the
whole transaction fee rate, not an allocated per-address fee or proven owner/device
policy. Counts refer to the address; self-payments can be receipts and spends.

| Feature | Nonmissing | Min | p50 | p95 | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `active_block_count` | 500 | 1 | 1 | 5 | 225 |
| `activity_span_blocks` | 500 | 0 | 0 | 104419 | 263284 |
| `balance_sat` | 500 | 14999770 | 40932154 | 500000294 | 2989252501 |
| `blocks_since_first_activity` | 500 | 3811 | 196543 | 264616 | 284468 |
| `blocks_since_last_activity` | 500 | 409 | 173735 | 261874 | 278905 |
| `confirmed_tx_count` | 500 | 1 | 1 | 6 | 225 |
| `median_spending_tx_fee_rate_sat_vb` | 18 | 1.00709 | 8.03265 | 100.29 | 100.29 |
| `receipt_tx_count` | 500 | 1 | 1 | 5 | 225 |
| `received_output_count` | 500 | 1 | 1 | 5 | 225 |
| `received_sat` | 500 | 14999770 | 41099710 | 507697893 | 2989252501 |
| `spending_tx_count` | 500 | 0 | 0 | 0 | 4 |
| `spent_output_count` | 500 | 0 | 0 | 0 | 29 |
| `spent_sat` | 500 | 0 | 0 | 0 | 557828665 |
| `unspent_output_count` | 500 | 1 | 1 | 4 | 225 |

Quantiles use the empirical inverse CDF (rank `max(1, ceil(p*n))` among observed
values); p50 is a lower median when n is even. Fee-rate values above are rounded
for display; the summary retains full numeric precision. Thirteen features have
500 observed values; spending fee rates have only 18. No feature is globally
constant and no two complete feature columns are identical. Nevertheless, most
count/span/spending fields have very little variation over most of the cohort.

There are six groups of identical fourteen-feature vectors, covering 13 rows.
These are distinct source identifiers with identical measured profiles, not
proven duplicate entities. They remain in the dataset. Prior receipts include
38 outputs of at most 1,000 sat, totalling 12,380 sat; these are retained without
assigning them an intent or calling the containing addresses low-value wallets.

## What this supports and the next unit

The cohort primarily describes addresses holding funds with little prior spending.
That is a useful source-side finding and a plausible feature hypothesis, but this
cohort alone cannot show that the behaviour is specific to theft or Coldcard.
The reference-spend outcome is a separate observation, not a device fingerprint.
Provider counter/pagination completeness is not cryptographic inclusion proof.

The next unit is a target and comparison protocol for the address model, using
this snapshot as the case cohort. Specify the observation unit, calendar/block
period, eligibility independent of model scores, provider/history completeness,
label provenance, related entities/incidents and candidate evaluation universe
before sampling. Avoid making a different collection window or missing-history
pattern the effective class label. Do not match away balance or holding age
without a specific scientific reason: those are candidate predictors.

For a **case-association** study, explicitly name its retrospective target and
retain uncertain background as unlabeled rather than certified legitimate. Such
comparisons can support descriptive contrasts; they cannot yield a validated
false-positive rate/F1 for theft or hardware identity. For claims about actual
theft/device detection, additional target-relevant evidence and evaluation on
independent groups are still required. A random address split within this one
incident does not establish cross-incident generalization. The solitary public
report is useful supporting evidence, not a representative validation sample.

## Reproduce

From the repository root, verify the committed bytes without private caches:

```bash
python "Task 2/research/coldcard/consolidate_source_dataset.py" verify \
  "Task 2/research/coldcard/source_dataset_20261030/protocol.json"
python -m unittest discover -s "Task 2/research/coldcard" -p "test_source_*.py"
```

`build` writes the same two outputs only where neither exists; use a copied
protocol under another directory within `research/coldcard` for a new output.
Inspect the JSON directly with Python:

```python
import gzip, json
from pathlib import Path
path = Path("Task 2/research/coldcard/source_dataset_20261030/view.json.gz")
data = json.loads(gzip.decompress(path.read_bytes()))
X = [[row["features"][name] for name in data["predictor_allowlist"]]
     for row in data["rows"]]
# X contains nulls (Python None); fitting/preprocessing is a separate experiment.
```
