# Reproduce and verify Task 2

All commands below run from the repository root. Use Python 3.12. No model needs retraining to read the saved results.

## CryptoBilis offline source readiness

```bash
python "Task 2/research/external_cases/build_cryptobilis_source_protocol.py" verify \
  "Task 2/research/external_cases/cryptobilis_source_readiness_20261102/configuration.json"
python -m unittest discover -s "Task 2/research/external_cases" -p test_cryptobilis_source_protocol.py
```

The standard-library implementation reuses the pinned collector snapshots and
Coldcard normalized checkpoints. It checks references, amounts, unknown labels,
source counts, partial overlaps and exact output fingerprints without provider
requests, source-feature extraction, scoring or model fitting. The next-stage
comparison plan is not an executed comparison selection. Full-prefix overlap and
verified victim/device labels remain unresolved.

## Current source-address write-up and frozen model

The [English research report](source_address_study/README.md) and its LaTeX
fragments are built from saved JSON, with a checked PDF already included.

```bash
python "Task 2/docs/build_source_address_study.py" check
python "Task 2/research/coldcard/train_source_membership.py" verify \
  "Task 2/research/coldcard/source_membership_baseline_20261102_162335/protocol.json"
```

The report checker uses the standard library and Pandoc 3.1.3; the model verifier
requires the exact versions pinned by the fitted protocol (including scikit-learn
1.8.0). Both commands perform no model fit and no provider request. They check
different layers: article text/tables versus fitted-tree score replay. The report
contains article integration and two-pass LaTeX compilation instructions. The
original Overleaf sources and live project are not modified. Old experiments
below retain their separate targets and reproduction commands.

## 1. Check the reorganized repository

```bash
python "Task 2/check_repository.py"
```

This checks Markdown links within Task 2, Python syntax and the protected artifact manifest. It makes no network requests and requires only the standard library.

## 2. Run the automated tests

Install the research dependencies if necessary, then run each suite in a separate process:

```bash
python -m pip install -r "Task 2/research/coldcard/requirements.txt"
python "Task 2/check_repository.py" --tests
```

The runner covers the Coldcard, external-case, wallet-storage, Elliptic++, Real-CATS and demo suites. It does not download data, train models or execute expensive experiments. Standard-library-only tests can also be run directly by directory if optional research dependencies are unavailable.

## 3. Run the offline demonstration

```bash
python "Task 2/run_demo.py"
```

The demo reads pinned saved artifacts and can apply the exported Coldcard tree. It never retrains a forest or evaluates reserved test sets. `verified` applies only to the named check. Missing data are reported as `missing`; out-of-scope or unavailable checks are `unchecked`; inconsistent inputs produce `failed` and a nonzero exit code.

With separately supplied datasets:

```bash
python "Task 2/run_demo.py" \
  --data-dir /path/to/coldcard_data \
  --history-dir /path/to/additional_histories \
  --real-cats-source /path/to/Real-CATS \
  --output /path/to/new_demo_report.json
```

The Coldcard directory must contain the checksum-verified `transactions.csv.gz`. Additional histories may include the separately supplied FSF file; `--history-dir` can be repeated. Real-CATS source data are the pinned BB.tsv and CB.tsv files. The program refuses to overwrite a report.

The demo recalculates available history features when the research dependencies are installed, but it does not reproduce forest inference. Its exact-address overlap check does not establish entity/incident independence; see the [historical overlap audit](supplementary/real_cats/EXTERNAL_INDEPENDENCE_AUDIT.md).

## 4. Reproduce a particular experiment

Follow the numbered part guide first. Each detailed report lists its inputs, command and output names. Use a new output path. The classroom tree, grouped transaction model and address-level supplementary benchmarks are separate targets and should not be mixed.

- [Part 1: fund flows](part_1_case_study/README.md)
- [Part 2: feature extraction and audit](part_2_dataset/README.md)
- [Part 3: course exercise](part_3_classifier/README.md)
- [Part 4: grouped validation](part_4_validation/README.md)
- [Supplementary benchmarks](supplementary/README.md)

## Historical verification is not a new run

[Historical verification artifacts](verification/historical_20261015/README.md) retain earlier complete runs: 493,571 CSV rows checked, 493,468 eligible rows replayed and eleven external histories reconciled. Replaying a tree on its own training data is not a generalization estimate. Those artifacts retain their original paths and code hashes; do not mistake an old test log for a current execution.

The fresh reorganization checks are described in [Verification](verification/README.md). Raw datasets removed by workspace maintenance must be recovered from the separately supplied files before rerunning full data experiments; repository-only checks remain available.
