# CryptoBilis-to-Coldcard source-membership transfer

[Completed results and verification](RESULTS.md) - prepared protocol and original code below.

## Prepared protocol, 9 November 2026

This new experiment follows Hugo's reported supervision feedback. It uses
October CryptoBilis for training and July Coldcard for evaluation, with a
single shallow tree fixed before fitting. It is retrospective reverse-time
source-membership transfer, not a prospective or untouched theft/device test.
The original Coldcard model, forward CryptoBilis results and all old data remain
preserved. Deep learning on graphs is the subsequent main modeling work;
this is a bounded tabular comparison.

The [protocol](protocol.json), implementation and eligibility manifest are
published before fitting. The preparation independently recomputes all 1,707
available 14-field vectors from 43,584 normalized address/transaction records
and rebuilds all 1,281 components from the 1,866 selected sources. Its partition
matches the previously independently verified overlap audit exactly.

## Direction-specific population

| Dataset / role | Case | Comparison | Total |
| --- | ---: | ---: | ---: |
| CryptoBilis: available training vectors | 122 | 207 | 329 |
| CryptoBilis: retained unavailable prefixes | 0 | 37 | 37 |
| Coldcard: eligible evaluation vectors | 499 | 567 | 1,066 |
| Coldcard: complete vectors quarantined for links to training incident | 1 | 311 | 312 |
| Coldcard: retained unavailable prefixes | 0 | 122 | 122 |

All selected sources contribute their known identity/reference links. Every
Coldcard member of a component spanning the training incident is quarantined
from evaluation, including indirect links. Twenty-two unavailable Coldcard
prefixes are also in cross-incident components; their primary exclusion stays
missing coverage. The single quarantined case is the previously documented
`cohort_0191`. The 54 complete CryptoBilis comparisons excluded in the old
forward evaluation are training observations in this reverse design; their
linked Coldcard observations are now excluded from evaluation instead.
Thus the old 275-row forward eligibility manifest cannot simply be reversed.

## Frozen method

Fit once on all 329 available CryptoBilis vectors, with Gini criterion, maximum
depth 3, minimum 20 samples per leaf, balanced training class weights and seed
42. The classification threshold is fixed at >=0.5. Each of the original 14
variables uses only its observed CryptoBilis-training median (zero only if an
entire column is missing), with 14 fixed missing indicators. Inputs to the tree
are float32. No internal split, tuning, threshold search, calibration or
all-cohort refit is used: all settings are fixed before the one fit. Training
metrics are resubstitution diagnostics only.

Comparators are the constant training prevalence and descending prior inactivity
and balance, with ranking metrics only. Report precision, recall, F1, AP,
ROC-AUC, confusion counts and every external error. Operational labels remain
incident-specific graph-source membership. Verified compromise, seed origin and
signing-device labels remain unknown. Strict height cutoffs exclude the whole
reference block and every future transaction from inputs.

## Coverage and interpretation

This is an exploratory result conditional on the current incomplete selection
and measured-link quarantine. Missing prefixes can conceal further links;
neither component separation nor a high score establishes entity independence.
The old forward F1 and this reverse experiment concern different fitted models,
targets and eligible populations and are not interchangeable estimates.

## Run and verify

From the repository root, after the protocol commit is published:

```sh
python "Task 2/research/external_cases/cryptobilis_to_coldcard_20261109/fit_model.py" "Task 2/research/external_cases/cryptobilis_to_coldcard_20261109/protocol.json" --repo-root . --published-protocol-commit PREPARED_COMMIT_SHA
python "Task 2/research/external_cases/cryptobilis_to_coldcard_20261109/repair_export.py" "Task 2/research/external_cases/cryptobilis_to_coldcard_20261109/protocol.json" --repo-root .
python "Task 2/research/external_cases/cryptobilis_to_coldcard_20261109/verify_results.py" "Task 2/research/external_cases/cryptobilis_to_coldcard_20261109/protocol.json" --repo-root .
python -m unittest discover -s "Task 2/research/external_cases/cryptobilis_to_coldcard_20261109" -p "test_experiment.py"
```

The standard-library verifier uses no fitting library or provider connection.
It replays every exported float32 tree score/path, recomputes training medians,
weighted node counts, tied-score AP/AUC and classification metrics, and checks
all errors and exclusions. Preparation and verification do not fit a model.
Historical private caches are not needed for this public normalized-evidence
experiment. New coverage work is tracked separately.
