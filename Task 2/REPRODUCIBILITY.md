# Reproduce and verify Task 2

All commands below run from the repository root. Use Python 3.12. No model needs retraining to read the saved results.

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
