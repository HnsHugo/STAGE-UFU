# Verification on October 15, 2026

This run uses snapshots collected on **October 14, 2026**. It is not a new observation of chain state on October 15. The historical results in `../case_flows_20261014/` and the raw data have been retained.

The historical calculation was first reproduced exactly: the recomputed JSON is byte-for-byte identical to `../case_flows_20261014/case_flows.json`. After the checks were added, all preexisting fields in that JSON also remain identical to those in the new report.

## Checks performed

| Check on real data | Result |
| --- | --- |
| Archive analyzed in two passes | 98 blocks, 493,571 unique TXIDs |
| Old `parents.json`, reconstruction of every row | 1,070 identical rows; 1,279 parents absent from the archive |
| Course-address history | 507 transactions, completed pagination and matching stable counters |
| Spent inputs compared with received outputs | 341 matching outpoints, totaling 56,202,666,941 satoshis |
| Transactions shared by the two provider formats | 505, with matching output values/addresses and block hash/height/date |
| Output-status snapshots for the five consolidations | 5 usable responses dated October 14, all `spent=false` |
| Automated flow tests | 15 tests passed, without network access |

The distinct sources of incoming transactions are **input addresses**, not people or victims. The 594.47728031 BTC received over the address's lifetime is not a demonstrated stolen amount. The selected consolidation consumes 562.02666941 BTC, creates 562.01962301 BTC in outputs and pays 0.00704640 BTC in fees. The 947-second interval refers to the provider's transaction timestamps, not a verified attack duration.

## Corrections and guarantees

Negative-amount formatting was corrected: a partial difference of -1 satoshi now displays as `-0.00000001 BTC`. Collection now respects the extension: plain JSON for `.json`, gzip for `.gz`. These corrections change none of the amounts in this case.

The analysis now rejects a divergent prior parent audit, a spent prevout missing from or differing from the received output, a contradictory block anchor between providers, and an inconsistent destination in an output-spend snapshot. The `collect-outspends` command makes output-status collection reproducible. It retains a collection error as an unknown observation and refuses to overwrite an existing file.

These checks concern consistency between files and provider observations. No signature, Merkle proof or proof-of-work chain has been verified. No model was trained.

## Input hashes

| File | SHA256 |
| --- | --- |
| `blocos(1).tgz` | `679fe208f9a807fdd38e9d64948c73581af3e99ca52fb707ce06937e67bc536d` |
| `parents.json` | `9e47396449d8ba65d7d6978c9e979bdfc3a4c47b3f3dfcb399fb535982c1d779` |
| `coldcard_target_history_20261014.json.gz` | `ee785d7c6116c33cc1578a3dd09722f68f49a2dc295f983fbeb710d93bc11950` |
| `coldcard_seed_outspends_20261014.json` | `db00c8767d7842573883a088d4e42ea6035f568f14bba5e0374772ccc7bd6ff0` |

## Reproduce

From `Task 2/research/coldcard`, use an output directory that does not yet exist:

```bash
python analyze_case_flows.py analyze '/path/to/blocos(1).tgz' new_output \
  --parents /path/to/parents.json \
  --history /path/to/coldcard_target_history_20261014.json.gz \
  --outspends /path/to/coldcard_seed_outspends_20261014.json
python -m unittest test_case_flows -v
```

The two collection commands documented in `CASE_FLOWS.md` produce new snapshots. Public conditions may change; these snapshots do not replace the October 14 files required to reproduce this report exactly.
