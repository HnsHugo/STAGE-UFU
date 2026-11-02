# Source comparison feasibility — 2 November 2026

Offline audit of the latest schema-v2 view. The unit is one selected input source address; the target is `known_coldcard_core_membership`. This is retrospective within-window case association, not verified theft or hardware identification. No provider request, model, fitted preprocessing or dataset split was performed.

## Coverage and attrition

| Reference block | Membership | Selected | Available | Unavailable | Coverage |
| --- | --- | ---: | ---: | ---: | ---: |
| All | case | 500 | 500 | 0 | 100.00% |
| All | comparison | 1000 | 878 | 122 | 87.80% |
| 960188 | case | 63 | 63 | 0 | 100.00% |
| 960188 | comparison | 126 | 108 | 18 | 85.71% |
| 960189 | case | 110 | 110 | 0 | 100.00% |
| 960189 | comparison | 220 | 179 | 41 | 81.36% |
| 960190 | case | 168 | 168 | 0 | 100.00% |
| 960190 | comparison | 336 | 300 | 36 | 89.29% |
| 960191 | case | 159 | 159 | 0 | 100.00% |
| 960191 | comparison | 318 | 291 | 27 | 91.51% |

All 1,378 available vectors reproduce exactly from the pinned normalized prefixes (35,323 address/transaction observations). The entire reference block and all future heights remain excluded. The 122 bounded-incomplete comparisons retain null vectors and remain outside this assessment's eligible population.

Membership prevalence changes from 33.33% in the selected cohort to 36.28% among available vectors. Completion is asymmetric by class and block. The following saved full-current-history counts help describe this selection effect; they were observed at different collection snapshots and are **not** pre-cutoff predictors or estimates for missing features.

| Comparison vectors | Count | Full-current transaction count p50 | p95 | Maximum |
| --- | ---: | ---: | ---: | ---: |
| available | 878 | 3 | 361 | 1564 |
| unavailable | 122 | 3347 | 1014156 | 5945884 |

The incomplete group cannot be assumed missing at random. These data support a complete-case exploratory study with an explicit coverage limitation, not an unbiased study of every selected source. A page bound does not establish the exact number of prior transactions. No unavailable vector was imputed, replaced or recollected.

Full-current-history coverage stays separate: 864 comparison histories are complete and 136 incomplete. Fourteen of the incomplete current histories have a validated exhausted prior prefix. The remaining 122 prior prefixes are bounded-incomplete. A prefix does not reconcile the current full-history counters.

## Frozen grouping and partition feasibility

The 1,378 eligible addresses form 918 connected components (840 singletons). The largest contains 284 comparisons. An independent breadth-first graph traversal reproduces every component. Groups combine repeated address hashes, shared prior transactions, common reference TXIDs and identical fourteen-feature vectors including missingness. They prevent measured overlap and do not establish common ownership.

| Link criterion | Shared groups | Addresses in shared groups | Star edges before transitive closure |
| --- | ---: | ---: | ---: |
| address | 0 | 0 | 0 |
| prior_transaction | 559 | 299 | 683 |
| reference_transaction | 62 | 376 | 314 |
| full_vector | 13 | 50 | 37 |

The original salt `coldcard-source-split-v1:42:` and lexical minimum address SHA256 determine each component bucket, modulo ten (0–6 train, 7 validation, 8–9 test). This dry run exports aggregate counts only; it does not create model datasets or per-row partition files.

| Prospective partition | Components | Cases | Comparisons |
| --- | ---: | ---: | ---: |
| train | 633 | 346 | 687 |
| validation | 99 | 56 | 55 |
| test | 186 | 98 | 136 |

**The frozen feasibility gate passes:** each partition has at least 20 members of each class, with zero measured link groups crossing partitions.
No seed reroll, group splitting or resampling was used. Links involving unknown histories of excluded sources are not claimed absent. Retain the selected eligible population and component evidence unchanged for any subsequently authorized baseline.

## Descriptive feature profiles

Quantiles use the empirical inverse CDF (rank max(1, ceil(p*n))); missing values are excluded. Medians below are descriptive only and were not fitted as imputation values.

| Prior-block feature | Case p50 | Comparison p50 | Case missing | Comparison missing |
| --- | ---: | ---: | ---: | ---: |
| confirmed_tx_count | 1 | 1 | 0 | 0 |
| receipt_tx_count | 1 | 1 | 0 | 0 |
| spending_tx_count | 0 | 0 | 0 | 0 |
| received_output_count | 1 | 1 | 0 | 0 |
| spent_output_count | 0 | 0 | 0 | 0 |
| received_sat | 41099710 | 1155000 | 0 | 0 |
| spent_sat | 0 | 0 | 0 | 0 |
| balance_sat | 40932154 | 240620 | 0 | 0 |
| unspent_output_count | 1 | 1 | 0 | 0 |
| active_block_count | 1 | 1 | 0 | 0 |
| activity_span_blocks | 0 | 0 | 0 | 21 |
| blocks_since_first_activity | 196543 | 558 | 0 | 21 |
| blocks_since_last_activity | 173735 | 9 | 0 | 21 |
| median_spending_tx_fee_rate_sat_vb | 8.03265306122449 | 2.0065619491302304 | 482 | 476 |

Full distributions, including zeros and tails, are in `summary.json`. Feature availability remains distinct from a legitimately undefined spending fee rate. No post-cutoff counters, reference-payment fields, identifiers, labels or collection artifacts enter the fourteen predictors.

## Decision and reproducibility

The numerical coverage/grouping gate supports a later prespecified shallow decision-tree baseline on the available vectors, conditional on explicit complete-case interpretation. This audit does not authorize or execute that model. It cannot validate theft/device detection: independently verified compromise and device labels remain unknown for every row; one owner report is preserved separately, and all cases come from one incident. No independent-incident generalization or untouched-test claim is justified.

Inputs and implementation are SHA256-pinned in `protocol.json`; redacted component membership, shared link evidence and prefix/counter joins are in `group_evidence.json.gz`. Old checkpoints and views are unchanged. `verification.json` fingerprints all generated outputs.

Reproduce from `Task 2/research/coldcard`:

```sh
python audit_source_comparison_feasibility.py verify source_comparison_feasibility_20261102_1603/protocol.json
python -m unittest discover -s . -p test_source_comparison_feasibility.py
```
