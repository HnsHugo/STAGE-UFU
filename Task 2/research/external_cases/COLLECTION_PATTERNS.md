# Collection-pattern pilot — 19 October 2026

## Question and status

Can an address-level, temporal description capture many sources converging on a
small set of recipients, without calling that pattern a hardware fingerprint?
The new extractor works with any compatible Bitcoin address history. It does
not change or retrain any historical classifier, including the frozen 19-feature
external model. The professor's code remains pending. A subsequent
[reference review](PROFESSOR_REFERENCES.md) establishes CryptoBilis as the intended
second incident without changing the original evidence flags or numerical results.

## Focused source screening

| Candidate | Primary source | Decision |
| --- | --- | --- |
| CryptoBilis, October 2026 | [Bitquery investigation](https://bitquery.io/investigations/ledger-cryptobilis-hack) | Two complete Bitcoin collection addresses are published. The professor-supplied references now establish the intended case; per-address device evidence remains unverified. A third listed address is treated as likely separate and excluded. |
| Ledger Connect Kit, December 2023 | [Ledger incident report](https://www.ledger.com/blog/security-incident-report) | Malicious JavaScript affecting EVM DApps; not a Bitcoin hardware-device training case. |
| Counterfeit Trezor, reported May 2023 | [Kaspersky device investigation](https://www.kaspersky.com/blog/fake-trezor-hardware-crypto-wallet/48155/) | Historical supply-chain example, not a new 2026 incident. No exact address/TXID established in the inspected article text; not imported. |

The first row is an incident-level source assertion, not independent device
evidence for each address. Linked Ledger posts could not be fetched (HTTP 403).
No hardware-control label or verified decision-time label is assigned.
The registry records publication/revision dates separately; the date when each
specific address was first published is unverified and stays null. Bitquery's
commercial historical export was not purchased.

## Actual observations and results

Two public Blockstream histories were collected on 19 October 2026, with **83 and
46 confirmed transactions**. Pagination exhaustion, stable before/after counters,
amounts and spent/received output counts all reconcile. This is provider-record
consistency, not cryptographic inclusion verification. Compact raw responses
(approximately 42 KB compressed in total) are saved with SHA256 hashes so the
analysis can be reproduced offline.

The experiment uses only transactions with confirmation timestamps strictly
before **10 October 2026, 00:00 UTC**. Later receipts are excluded.

| Measured feature | `bc1qjq…49dl` | `bc1qqn…jtm9` |
| --- | ---: | ---: |
| Receipt transactions before cutoff | 76 | 46 |
| Gross BTC received before cutoff | 92.50620930 | 111.28199071 |
| Distinct input addresses in funding transactions | 76 | 46 |
| External funding transactions with exactly one output | 76 | 46 |
| Receipt confirmation span, seconds | 1,285 | 0 |
| Largest single-block share of receipts | 85.53% | 100% |
| Median incoming transaction fee rate, sat/vbyte | 198.1818 | 208.0909 |
| Spending transactions before cutoff | 0 | 0 |

These are **122 receipt transactions and 203.78820001 BTC**, not 122 independently
verified victims or hardware devices. A zero-second span means the same block
timestamp, not simultaneous signing or broadcasting. Incoming fee rates describe
funding transactions, not the receiver's own fee-setting policy. Exactly one
output does not prove that every UTXO controlled by the source was drained.

Seven later transactions into the first address add only 3,853 satoshis to the
full collected history. They are excluded from the historical prefix. This
illustrates why a complete current history must not be used indiscriminately to
describe the incident or make a historical prediction. Their roles remain unknown.

## Relation to the existing Coldcard work

The [saved Coldcard flow report](../coldcard/case_flows_20261015/CASE_FLOWS.md)
already establishes a collection/consolidation structure: one selected
consolidation consumes 341 received outputs. By contrast, neither new address
has an observed spend before the chosen cutoff. Therefore a rule requiring an
onward consolidation would miss both at that date. This is a descriptive
difference between case observations, not an ML false-negative measurement.

The Coldcard whole-history span and this one-day incident prefix use different
observation policies; do not compare their durations as matched features. A
future comparison must run the same extractor with prespecified windows and
prediction times for both cases, plus suitable comparison groups.

## Interpretation and next experiment

The pilot demonstrates that a collection motif is measurable with actual data.
It does not establish discrimination from exchange deposits, donations or other
legitimate collection behavior. The two recipients share one provisional case
group and must stay together in any split. Unknown background is not certified
legitimate. No accuracy, F1 or calibrated theft probability is reported.

Next: apply the same observation protocol to the Coldcard case and documented
comparison recipients, retain source/entity/incident groups, and compare simple
temporal/graph baselines. Keep this provisional case outside training until its
role evidence and the research target are agreed. A detector for collection-like
behavior is a different target from recognizing a hardware brand.

## Reproduction

From `Task 2/research/external_cases`, using a new output filename:

```bash
python collection_patterns.py analyze hardware_case_registry_20261019.json \
  collection_pilot_20261019 2026-10-10T00:00:00Z /tmp/new_collection_patterns.json
python -m unittest discover -p 'test_*.py' -v
```

For a new public collection, use a new path. New snapshots can differ from the
saved observations and must keep their own checksums and collection timestamps:

```bash
python collection_patterns.py collect \
  bc1qjqgwejnp8dc0x2938x9n9954hj97t82unx49dl /tmp/new_first_history.json.gz
```

The [registry](hardware_case_registry_20261019.json) stores complete addresses and
the retrieved source-page hash. The [result](collection_pilot_20261019/patterns_asof_20261010.json)
stores raw-history hashes, provider audits, exact values and interpretation limits.

Verification: all **150 tests** passed across the six offline suites, including
12 new boundary/reproduction tests. Repository checks validated 136 internal
links, 80 Python files and 185 unchanged historical artifacts. The execution log
is [saved separately](../../verification/collection_patterns_20261019.json).
