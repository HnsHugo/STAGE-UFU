# Equal-duration collection comparison — 19 October 2026

## Research question

Which collection-pattern measurements persist across the Coldcard and provisional
CryptoBilis observations, and how do they compare with a documented donation
recipient? This extends the address-tracing work without choosing a hardware
classifier or fitting on unresolved labels.

Subsequent [professor-supplied references](PROFESSOR_REFERENCES.md) confirm the
choice of CryptoBilis as the second incident. Historical result identifiers and
provisional address-evidence fields remain unchanged.

## Data and selection

- Coldcard: a new public history of the course address, collected separately from
  historical artifacts. Use the UTC calendar day 30 July 2026.
- CryptoBilis: reuse the two pinned histories from the
  [first collection pilot](COLLECTION_PATTERNS.md). Use 9 October 2026; the two
  addresses remain in one provisional incident group.
- EFF: reuse the existing provider-complete, SHA256-pinned donation history.
  Official-purpose evidence is recorded in the
  [comparison selection](donation_comparison_selection_20261014.json).
  Use both incident calendar days, including any day with no receipt. Also include
  the UTC day with the most receipts strictly before 10 October; break ties by
  earliest date. This is a disclosed retrospective stress window, not a date a
  prospective detector could select in advance.

Every activity window is **24 hours**, with inclusive start and exclusive end.
Features use provider block timestamps. Pre-window funds affect the balance
before the cutoff but not the window's receipt counts, amounts, fee rates or
spending activity. Current UTXO status and later transactions are not features.
The original prefix-only pilot still reproduces exactly.

Registry selection is based on documented roles and available complete data,
not on a classifier's scores. The incidents' first-day windows are retrospective
choices, not a test of advance incident discovery. Equal duration does not match
address maturity, transaction volume, market fee conditions or calendar date.
One EFF recipient is a convenience comparison; its donation purpose does not
certify every incoming fund or imply an absence of compromise.

## Results

Exact measurements, raw-history hashes, source/group metadata and pairwise
transaction/input-address overlaps are in
[comparison.json](collection_comparison_20261019/comparison.json).

| Observation | UTC day | Receipts | Gross BTC received | One-output receipt share | Receipt span (s) | Largest-block share | Spends |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Coldcard course collector | 2026-07-30 | 500 | 594.47722484 | 100.00% | 918 | 33.60% | 1 |
| Provisional CryptoBilis 1 | 2026-10-09 | 76 | 92.50620930 | 100.00% | 1285 | 85.53% | 0 |
| Provisional CryptoBilis 2 | 2026-10-09 | 46 | 111.28199071 | 100.00% | 0 | 100.00% | 0 |
| EFF donation recipient | 2026-07-30 | 1 | 0.00003416 | 100.00% | 0 | 100.00% | 1 |
| EFF donation recipient | 2026-10-09 | 0 | 0.00000000 | n/a | n/a | n/a | 0 |
| EFF donation recipient (stress window) | 2024-12-06 | 2 | 0.00407592 | 0.00% | 4672 | 50.00% | 1 |

**Observed counterexample:** on 30 July, EFF also has a one-output receipt and
100% of its receipts in one block. With only one receipt, these ratios are
trivial; neither property alone distinguishes a reported incident from ordinary
donation collection. The case collectors differ strongly in receipt volume in
this tiny sample, but it is not a volume-matched control population.

Coldcard has one onward spend within its selected day, while the provisional
CryptoBilis collectors have none. Requiring a downstream consolidation would
exclude both provisional recipients at their cutoff. A uniform spend rule is
therefore not a demonstrated cross-case invariant.

The EFF stress window is 6 December 2024 and contains only two receipts. It
does not represent a busy exchange or high-throughput service. Calendar date
and market fees also differ; incoming fee rates must not be interpreted as a
hardware fingerprint.


## Scientific interpretation

These are descriptions of two source-attributed incidents and one documented
comparison entity. The multiple EFF windows are repeated observations of one
entity; the two CryptoBilis recipients are not two independent incidents.
Observed source addresses are not counts of victims, people or hardware devices.
Input-address co-occurrence does not allocate value among a transaction's outputs.
One-output receipts do not establish that every source UTXO was consumed.

No threshold is optimized, no classifier is trained and no F1, precision or
independent detection accuracy is claimed. The frozen external model is unchanged.
Exact address/TXID non-overlap alone does not establish common-ownership or entity
independence. Historical address-label availability and per-address hardware
control remain unknown.

## Reproduction

From `Task 2/research/external_cases`, choose a new result path:

```bash
python compare_collection_patterns.py collection_comparison_20261019/registry.json \
  /tmp/new_temporal_collection_comparison.json
python -m unittest discover -p 'test_*.py' -v
```

The registry resolves raw-history paths relative to itself and refuses changed
checksums, mismatched addresses, incomplete provider counters or invalid history.
The saved small Coldcard history allows offline reproduction; existing EFF and
CryptoBilis observations are reused without duplicating their raw files.

Verification: **159 tests pass** across the six offline suites, including nine
new window/comparison tests. All 185 protected historical artifacts retain their
hashes. The [execution report](../../verification/temporal_collection_comparison_20261019.json)
records the actual run. No cross-group transaction or input-address overlap was
observed in these selected windows; this does not prove entity independence.

## Next priority

Expand documented comparison entities and collection contexts before evaluating
discrimination. Preserve complete incident/entity groups across any future
training/validation/test split. Define the final prediction target and obtain
participant/device evidence before constructing hardware-related training labels.
A graph or temporal collection detector remains a different target from device identification.
