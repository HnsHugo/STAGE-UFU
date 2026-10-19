# Preserved results and recovery checks

These experiments ran before the 16 October 2026 UTC recovery. No model was retrained during that recovery or as part of the later directory reorganization.

- `demo.json`: the earlier full offline demo, including its explicit unchecked items.
- `grouped_metrics_reproduced_20261014.json`: copied metrics from the earlier grouped-experiment reproduction.
- `external_scores_reproduced_20261014.json`: the eleven external scores/features from the earlier frozen-model reproduction.
- `recovery_tests_20261016.json`: commands and outputs of the 106 tests rerun during recovery.

Raw datasets remain outside Git. The separate `coldcard_case_evidence_20261015.zip` includes the target history, five output observations, manifest and instructions. Its presence and ZIP integrity were checked during recovery; SHA256 is `52c4f9bdb8c4de0415275934b229b96aa3109495c7bbcae58239f58cecd5b379`.

The separately supplied FSF history has SHA256 `133144439843f6407c4e797b79db4c12205bbcb3c6fd510c2ca778e9aa64eae9`.

Recorded paths and script hashes describe the original executions. File checks and tests do not certify label truth or cryptographic inclusion in the blockchain. See [current verification](../README.md) for reorganization checks.
