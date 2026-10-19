# Feature analysis — 8 October 2026

## Validation

Extraction provided by Hugo from Codespaces. Manifest status complete: 493,571 observations and 493,571 unique TXIDs, with no duplicates. The 98 coinbase transactions are distinguished. For every other transaction, total input value minus total output value equals the reported fee.

SHA256 of transactions.csv.gz: `158788226288dce22bfd5ea20deab1b72551c5d0c32bdb547e113c83273841b4`.

| Provenance group | Count | Median output count | Median fee rate, sat/vB |
|---|---:|---:|---:|
| Source-attributed | 5 | 1 | 5.0092 |
| Direct parent candidates | 1070 | 1 | 30 |
| Unattributed | 492496 | 2 | 0.4429 |

Median fee rates exclude coinbase transactions. Candidates are not confirmed thefts; unattributed transactions are not certified legitimate transactions.

## Concentration and descriptive rules

Candidates occur in six blocks: 960183 (204), 960185 (491), 960188 (63), 960189 (110), 960190 (168), 960733 (34). They do not constitute 1070 independent cases.

All candidates have one output; 934 have one input and one output. The unattributed group also contains 54,510 one-output transactions, including 39,493 with one input. This shape is insufficient to establish theft.

The descriptive rule “one output and fee rate >= 4.95 sat/vB” selects 1070 candidates, but also 7231 unattributed transactions and 3 of the 5 attributed consolidations. The threshold was selected after inspection: these counts are descriptive, not an out-of-sample evaluation. The 7231 transactions cannot be declared confirmed false positives or newly discovered thefts.

## Decision-tree protocol

An initial tree may distinguish parent candidates from the unattributed background: its target must explicitly be named relation to the case, not confirmed theft or hardware-wallet control. The five consolidations represent a separate role and must not automatically be mixed with collection transactions.

Before reporting performance: complete provenance groups (descendant consolidation, collector, connected component), prevent related groups from appearing in both training and test, reserve the test set before tuning hyperparameters, exclude TXID/height/relation from predictive features, and report precision/recall/F1 as proxy-target metrics. Grouping by block alone does not guarantee collector independence.

A tree that reproduces this case does not demonstrate detection of new thefts. External validation with documented cases and sourced controls remains necessary. This report does not claim trained-model performance.
