# Real-CATS Hack/Theft source-category benchmark

## Objective and data

Classify the original Real-CATS Hack/Theft categories against its benign comparison pool. This is an offline source-label experiment, not independently verified stolen-fund detection. See PROVENANCE_REVIEW.md for unresolved incident roles and the authors' benign-selection assumption.

Pinned source: https://github.com/sjdseu/Real-CATS/tree/054c659412a07d1dac596f625d02a84039f22a9b
Publication: https://arxiv.org/abs/2501.15553
Both TSV files are checksum-verified against the earlier download manifest.

The dataset contains 87,894 active address profiles: 711 Hack, 600 Theft and 86,583 benign. Addresses are unique, and no benign/criminal address overlaps are accepted. Other crime categories and zero-transaction addresses are excluded rather than recoded benign.

Twenty-two numerical profile features are used. Address, label, absolute first/last timestamps, transaction IDs, verification flags and all USD features are excluded. Lifetime and aggregate monetary features remain under an explicitly offline interpretation. The 28,032 missing/nonfinite numeric cells are replaced by column medians fitted on training only. There are no entirely missing training columns. Imputation can introduce source artifacts and is not a reconstruction of missing blockchain observations.

## Splits and model selection

Unique addresses are sorted, then stratified by the three original categories into 60/20/20 splits, using random states 42 and 43.

| Set | Addresses | Hack | Theft | Benign |
| --- | ---: | ---: | ---: | ---: |
| Training | 52736 | 427 | 360 | 51949 |
| Validation | 17579 | 142 | 120 | 17317 |
| Test | 17579 | 142 | 120 | 17317 |

Two predefined models are fitted to training only: a depth-8 decision tree and a 100-tree random forest with max_depth=20, max_features=sqrt and bootstrap samples. Both use min_samples_leaf=20, positive class weight 3 and random_state=42. Nineteen predefined thresholds (0.05 to 0.95) are compared on validation. Maximum validation F1 chooses model and threshold. The reserved test is then evaluated once with no refitting or post-test adjustments.

## Results

| Model | Selected validation threshold | Validation precision | Validation recall | Validation F1 |
| --- | ---: | ---: | ---: | ---: |
| Decision tree | 0.35 | 19.90% | 30.92% | 24.22% |
| Random forest | 0.30 | 34.95% | 27.48% | 30.77% |

The forest is selected. On held-out test addresses:

| Measure | Result |
| --- | ---: |
| Precision | 40.63% |
| Recall | 29.77% |
| F1 | 34.36% |
| Average precision | 30.64% |
| True positives | 78 |
| False positives | 114 |
| False negatives | 184 |
| True negatives | 17203 |

Among positive test categories, 36/142 Hack and 42/120 Theft references are recovered. Positive prevalence is about 1.49%; an always-benign baseline has zero precision/recall/F1 and average precision equal to prevalence. Model scores are not calibrated probabilities.

## Interpretation

This is a substantially less favourable benchmark result than Elliptic++, but targets, feature schemas, populations and class prevalence differ. The models were separately trained: this does not measure cross-dataset performance of the original Elliptic++ forest, and percentage differences must not be interpreted as a controlled generalization drop.

Address-disjoint splitting does not establish entity or incident independence; case IDs are not available. Full-history features are not available at a historical prediction time. Report categories are not independently verified theft roles, and the benign pool carries a source-selection assumption. These limits prevent a claim of operational theft detection.

The low recall is a useful baseline to retain rather than erase through test-driven tuning. Next work should assess validation errors and missing-value patterns, strengthen source provenance and construct incident-disjoint decision-time data. The inspected test must not become a tuning target.

## Reproduction

Use Python 3.12 and the pinned dependencies:

```bash
python -m pip install -r requirements.txt
python train_source_categories.py /path/to/Real-CATS /path/to/new_output
python -m unittest discover -p 'test_*.py' -v
```

Download BB.tsv and CB.tsv from the pinned source URLs in ../theft_cases/research_download_manifest.json. The output directory must be new. Committed results contain metrics.json, status.json and readable decision-tree rules. The script also writes split_assignments.csv.gz locally, omitted from Git; logical assignments are reproducible while gzip byte hashes may depend on timestamps. No fitted production model is exported.

Three tests cover exclusion of other categories/inactive addresses, conflicting-label rejection and disjoint/exhaustive three-way splitting. The real run's split counts and confusion totals were independently checked.

## Diagnostic de validation du 18 octobre 2026

Le [diagnostic par catégorie et valeurs manquantes](VALIDATION_ERRORS_20261018.md) reproduit les métriques du benchmark à 22 caractéristiques. Sur 190 omissions de validation, 187 concernent des profils complets. Le test réservé et la forêt externe figée ne sont pas évalués par ce diagnostic.
