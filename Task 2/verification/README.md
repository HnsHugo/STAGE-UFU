# Verification and historical evidence

## Current repository checks

Run `python "Task 2/check_repository.py" --tests` from the repository root. This verifies internal documentation links, Python syntax, preserved artifact hashes and all six test suites without training a model.

The reorganization check report is `reorganization_20261019.json`. It is generated after the move and translations; it records the checks actually executed. Missing separately supplied datasets are not treated as newly reproduced experiments.

## Historical executions

[historical_20261015/](historical_20261015/README.md) contains the earlier demo and recovery/reproduction outputs. Their numbers, code hashes and recorded paths are historical evidence, not descriptions of the current layout. Original logs remain unchanged.

The [artifact manifest](../docs/ARTIFACT_MANIFEST.json) protects pre-reorganization JSON, CSV, compressed evidence and readable tree files. Documentation and path-maintenance code are allowed to change; scientific values and raw bytes are not silently replaced.

The [30 October comparison recovery checks](comparison_recovery_20261030.json)
record the 233 newly complete histories, raw re-extraction, preservation of the
original results, the persistent HTTP 429 after cooldown and the combined
1,500-row snapshot. Collection is stopped; this is not a completed comparison
dataset or a model validation result.

The [later retry milestone](comparison_retry_milestone_20261030.json) records
original-route access restored, 70 further complete histories in the first four
batches, unchanged earlier snapshots and 86 passing source-path regressions.
The collector continued beyond that historical milestone.
