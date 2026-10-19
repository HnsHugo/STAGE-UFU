# Data access and file types

## What Git contains

The repository contains code, source registries, selected saved histories, small cohorts, readable trees, numerical metrics and documentation. The reorganization preserves existing scientific file bytes; [the artifact manifest](docs/ARTIFACT_MANIFEST.json) records their hashes at the new paths.

## Separately supplied inputs

These files were used in earlier verified runs but are not guaranteed to exist in a fresh checkout. Keep original bytes and choose new output folders.

| File | Purpose | SHA256 |
| --- | --- | --- |
| `blocos(1).tgz` | The 98 selected raw blocks | `679fe208f9a807fdd38e9d64948c73581af3e99ca52fb707ce06937e67bc536d` |
| `transactions.csv.gz` | 493,571 extracted transaction rows | `158788226288dce22bfd5ea20deab1b72551c5d0c32bdb547e113c83273841b4` |
| `parents.json` | Recovered parent audit | `9e47396449d8ba65d7d6978c9e979bdfc3a4c47b3f3dfcb399fb535982c1d779` |
| `coldcard_target_history_20261014.json.gz` | Complete saved course-address history | `ee785d7c6116c33cc1578a3dd09722f68f49a2dc295f983fbeb710d93bc11950` |
| `coldcard_seed_outspends_20261014.json` | Dated observations for five outputs | `db00c8767d7842573883a088d4e42ea6035f568f14bba5e0374772ccc7bd6ff0` |
| `fsf_history_20261014.json.gz` | Full FSF pilot history | `133144439843f6407c4e797b79db4c12205bbcb3c6fd510c2ca778e9aa64eae9` |

The Coldcard history and output observations were also delivered in `coldcard_case_evidence_20261015.zip`, SHA256 `52c4f9bdb8c4de0415275934b229b96aa3109495c7bbcae58239f58cecd5b379`. Recover the original supplied archive for exact reproduction. A later public-API collection is a new snapshot and may differ.

A committed copy of candidate groups is available in [the Coldcard input folder](research/coldcard/inputs_20261008/candidate_groups.json); the matching manifest is [here](research/coldcard/inputs_20261008/manifest.json).

Real-CATS and Elliptic++ raw feature tables are separate public-source downloads. Their pinned source URLs, checksums and procedures remain in [the download manifest](research/external_cases/research_download_manifest.json) and the relevant [supplementary reports](supplementary/README.md). Do not spend time downloading them just to read the main Coldcard results.

## How to read the files

| Extension | Meaning |
| --- | --- |
| `.md` | Human-readable explanation: start here |
| `.py` | Executable script or automated test |
| `.json` | Structured source metadata, audit or metrics; inspect the matching report first |
| `.csv` | A table, such as the 200-row course cohort |
| `.txt` | Readable tree rules or requirements, depending on the filename |
| `.gz` / `.tgz` | Compressed inputs or histories; not all are committed |

Historical JSON fields may contain the old directory names. They record the original execution. Current commands and runtime paths are documented in the English reports, not retroactively rewritten into evidence files.
