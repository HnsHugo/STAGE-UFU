# Coldcard source-address evidence registry — 27 October 2026

## Question and executed result

This unit implements the next aligned stage: reconstruct the **input/source
addresses**, not another collector ranking. One registry row represents an
observed address, linked to its payment inputs and previous outpoints. No model
was fitted, no score/threshold was changed, and no train/test split is claimed.
All rows retain the same `coldcard_2026` incident group; entity identity is unknown.

The existing complete collector history collected on 19 October was reused.
Its SHA256 is
`955ac9ecd6a88dc40121f46aee02841aa9facdb1969c3fb2215657eaeb9af535`.
This is the later pinned history already committed under external cases, not the
separately supplied 14 October history with a different checksum. There was no
new API collection in this unit.

| Observation | Candidate day: 30 July UTC | Outside the candidate day |
| --- | ---: | ---: |
| Incoming transactions | 500 | 6 |
| Distinct input addresses | 500 | 5 |
| Non-coinbase input observations / spent previous outputs | 1,324 | 7 |
| Gross receipts at the collector, satoshis | 59,447,722,484 | 5,547 |
| Funding input total, satoshis | 59,451,379,184 | 352,581 |
| Transaction fees, satoshis | 3,656,700 | 4,263 |
| Missing input addresses or prevout records | 0 | 0 |
| Collector receipt outputs consumed in the saved consolidation | 341 | 0 |

There are **505 distinct observed input addresses and 1,331 input evidence
records** overall, with no address overlap between the two windows. Later inputs
are retained separately and are not assigned legitimate labels. The complete
507-transaction history also contains the collector's outgoing consolidation;
its collector inputs do not become original source-address records.

All 500 candidate-day payments have one distinct input address and one output.
419 spend one previous output, while **81 spend multiple previous outputs** from
the same decoded address; one uses 200 inputs. Every candidate address appears
in exactly one such payment. Thus 1,324 inputs are not 1,324 addresses or victims.
The pattern is consistent with consolidation/sweep-shaped payments but does not
prove that every UTXO of a wallet was drained or identify a signing device.

Candidate-day receipts confirm from **01:36:08 to 01:51:26 UTC**, a span of
918 seconds. This is a confirmation span, not an established attack/broadcast
duration. The protocol uses the existing case's whole UTC day as a retrospective
candidate interval; an independently verified exact theft start/end is missing.
Gross receipts of 594.47722484 BTC and fees of 0.03656700 BTC are measured flows,
not independently certified stolen amounts. Outside-window transactions have
multiple outputs in some cases: their total input values must not be allocated
entirely to the collector's much smaller receipt.

## Three separate evidence dimensions

1. **Observed relation:** each source observation links an address to a payment
   TXID/input index, previous TXID/output index, value, block anchor, confirmation
   date, collector receipt output and observed subsequent collector spending.
   Provider URL, collection date and review date are retained.
2. **Reported/verified compromise:** case context supports investigating the
   payments, but no address-specific compromise evidence was supplied to this
   extractor. `compromise_status` stays `unknown`, its evidence list is empty,
   and the supervised label/availability date stay null.
3. **Hardware-wallet control:** the mechanism is described by the professor's
   references, but this does not establish the device behind each input address.
   Hardware status/confidence remain unknown and its supervised label stays null.

Consequently **zero verified compromised-source labels and zero verified
hardware-source labels** are claimed. This is a completed graph-evidence registry,
not yet a ground-truth training dataset. The source addresses' complete histories,
legitimate control cohort and independent incident evaluation are also missing.

## Files and field interpretation

- [Protocol](../source_registry_protocol_20261027.json): exact input checksum,
  interval, context URLs, unresolved publication dates and label policy.
- [Aggregate summary](summary.json): counts, timing, reconciliation and exact
  hashes/byte sizes of the generated detailed files.
- `addresses.json` (generated locally): one row per observed address, role,
  incident group, scopes, dates, confidence, unknown labels, input value totals
  and links through `evidence_ids`.
- `input_evidence.jsonl` (generated locally): one row per non-coinbase payment
  input, including previous outpoint and collector-output links. No receipt value
  is allocated to an individual input by assumption.

The detailed files are ignored by Git rather than republished as a new bulk list
of alleged victims. They are deterministically regenerable from the already
committed pinned history. All source identities and outpoints remain available
in the generated local registry; the summary does not pretend to anonymize an
underlying public blockchain.

Source prevouts are the provider's reported records; the upstream transactions
were not independently retrieved or cryptographically verified. Separately, all
341 consumed **collector** outputs reconcile with their received outputs in the
complete history. Stable counters and this outpoint check are not cryptographic
block-inclusion proofs. Later consolidation links are retrospective evidence,
not permissible future information for a pre-transfer predictor.

## Reproduction and checks

From the repository root, use a new output directory:

```bash
python "Task 2/research/coldcard/build_source_registry.py" build \
  "Task 2/research/coldcard/source_registry_protocol_20261027.json" \
  "Task 2/research/coldcard/source_registry_reproduction_20261027"

python "Task 2/research/coldcard/build_source_registry.py" verify \
  "Task 2/research/coldcard/source_registry_protocol_20261027.json" \
  "Task 2/research/coldcard/source_registry_reproduction_20261027"

python -m unittest discover -s "Task 2/research/coldcard" -p 'test*.py'
python "Task 2/check_repository.py"
```

`build` refuses an existing output directory. `verify` re-derives and compares
every output byte, including detailed-file hashes. The extractor rejects a changed
history checksum, unstable/incomplete counters, duplicate spent outpoints,
missing previous identifiers, noninteger/negative values and unreconciled fees.
Missing prevout/address data are counted rather than invented. Focused tests
cover window boundaries, repeated inputs, source/collector separation, unknown
labels, multiple-address inputs and input-order independence. The
[execution record](../../../verification/source_registry_20261027.json) records
the actual checks run for this unit.

## One next aligned unit

Build a small, deterministic pilot of **pre-payment address-history features**
from candidate sources, cutting off each history before its observed payment.
Document coverage and feature definitions first; keep this retrospective source
cohort distinct from verified compromised/hardware labels. Do not restart
recipient ranking or substitute an unrelated benchmark.
