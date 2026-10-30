# External corroboration of the 500 source addresses — 30 October 2026

## Executed improvement

All 500 fixed cohort sources were compared against two newly located public
reconstructions. The observation unit is a source address linked to its exact
reference payment. The target is externally attributed **case relationship**,
kept separate from independently verified unauthorized taking, hardware seed
origin and device use at signing. No model or control cohort was introduced.

The [protocol](../source_corroboration_protocol_20261030.json) was fixed before
comparison. It pins all local input hashes and the external Git commits/blob
hashes. The [per-source comparison](comparison.json) publishes cohort IDs and
identifier hashes, without republishing the external bulk address lists.

## Actual agreement

| Check | Sources agreeing / compared |
| --- | ---: |
| Exact address in SomaxBT's published list | 500 / 500 |
| Gross input value and input count in that list | 500 / 500 |
| Address/payment/block/collector and input-value multiset | 500 / 500 |
| Payment anchors, integer amounts, input/output counts and fees in Alvaro P.'s reconstruction | 500 / 500 |
| Sources corroborated by both reconstructions | **500 / 500** |

The input comparison covers **1,324 input observations**, totaling
**59,451,379,184 satoshis**. This is gross input value, not a certified stolen
amount. External previous-outpoint TXIDs/indexes are absent from the SomaxBT CSV:
input-value multiset agreement must not be described as independent verification
of all exact outpoints. Rounded fee rates were not compared; integer fees were.

## Sources and attribution

- [SomaxBT, `coldcard-drain-addresses`](https://github.com/somaxbt/coldcard-drain-addresses/tree/1e7fef87060808c29beaf9d137eb5ff9e37f8811):
  `victims/waves-1-3.csv` and `victims/waves-1-2-per-utxo-evidence.csv`.
  The author describes a chain reconstruction and explicitly distinguishes it
  from proof of theft or device origin. No victim-report ground truth is claimed
  for these rows. No repository license file was present in the reviewed tree;
  the original CSV files are retained locally, not redistributed here.
- [Alvaro P., `coldcard-weak-rng-research`](https://github.com/alva-p/coldcard-weak-rng-research/tree/f93cfed16302bb91c8409fdee9ce5576a34b7e52):
  `evidence/onchain/drain-transactions.csv` and `methodology.md`.
  The documented method traces backward from the reported consolidation and
  matches transactions by collector and block range. It explicitly does not
  establish an individual device or compromise mechanism. Documentation is
  identified by the repository as CC BY 4.0; source code as MIT.

Both authors describe separate reconstructions, and their APIs/methods can be
compared with ours. All nevertheless observe the same Bitcoin chain and use
collector/graph criteria. Agreement is corroboration of the reconstruction,
not three independent owner confirmations. Ancestry beyond the reviewed methods
was not verified. Git commit times identify source versions, not proven public
label-availability dates. The protocol records those availability dates as unknown.

The discovery search also found Coldcard Entropy and Coldcard Watch. The former
returned 502 on direct opening; no snapshots from either are used in these results.

## What improves, and what remains unknown

The new evidence layer upgrades all 500 case relationships from our original
`graph_candidate` observation to **`source_attributed`**: exact identifiers and
matching measurements are externally published. This follows the existing
[label protocol](../LABEL_PROTOCOL.md); it does not change the historical
registry, feature rows or previous point-in-time eligibility reports.

Individually verified compromise, hardware seed origin and hardware signing
labels remain null. External uses of “victim” or confidence “high” are author
assertions, not calibrated probabilities or owner/device confirmation. The
fourteen pre-payment predictors remain unchanged. Payment/corroboration facts
are retrospective case evidence and must not be inserted into those predictors.
There is still one incident group and no independently documented negative
control cohort; no validated supervised theft/hardware detector was fitted.

The earlier five-address exact-search pilot remains a valid record of its
limited queries, but is not the latest evidence coverage. The present comparison
provides a source-attributed case layer for all 500 addresses.

## Verification and reproduction

The [verification journal](../../../verification/source_corroboration_20261030.json)
records snapshot fingerprints, reproduction and regression/integrity checks.
Seven new tests reject wrong payments, blocks and collectors, equal-total but
different input multisets, duplicate/ambiguous rows, one-satoshi differences and
unsupported label promotion.

Retrieve the protocol's four `sources[].url` files at their pinned commits into
a local directory using `sources[].local_file` filenames. Keep the original
bytes, including CSV line endings; both SHA256 and Git blob hashes are checked.
Then, from the repository root:

```bash
python "Task 2/research/coldcard/corroborate_sources.py" verify \
  "Task 2/research/coldcard/source_corroboration_protocol_20261030.json" \
  "Task 2/research/coldcard/source_cohort_work_corroboration_20261030" \
  "Task 2/research/coldcard/source_corroboration_20261030"
```

No network request or model fitting occurs in this command. A fresh checkout
requires the pinned external snapshots; the ignored local copies are not in Git.

## Next aligned unit

Review the public owner-confirmed/report-based records identified by the new
sources and test whether exact identifiers overlap this fixed cohort. Preserve
their distinct incident/wave and evidential status. A reported case relationship
can support an explicitly defined provisional case-association study with
appropriate controls, but cannot silently become a verified hardware/theft target.
