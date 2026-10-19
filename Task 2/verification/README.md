# Verification and historical evidence

## Current repository checks

Run `python "Task 2/check_repository.py" --tests` from the repository root. This verifies internal documentation links, Python syntax, preserved artifact hashes and all six test suites without training a model.

The reorganization check report is `reorganization_20261019.json`. It is generated after the move and translations; it records the checks actually executed. Missing separately supplied datasets are not treated as newly reproduced experiments.

## Historical executions

[historical_20261015/](historical_20261015/README.md) contains the earlier demo and recovery/reproduction outputs. Their numbers, code hashes and recorded paths are historical evidence, not descriptions of the current layout. Original logs remain unchanged.

The [artifact manifest](../docs/ARTIFACT_MANIFEST.json) protects pre-reorganization JSON, CSV, compressed evidence and readable tree files. Documentation and path-maintenance code are allowed to change; scientific values and raw bytes are not silently replaced.
