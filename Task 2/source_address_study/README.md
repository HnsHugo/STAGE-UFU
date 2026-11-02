# Coldcard source-address study

English research write-up of the fixed dataset and membership baseline. The two LaTeX fragments follow the supplied article's `Our Work` and `Results` sections. This is new text for integration; the live Overleaf project and the originally supplied files were not modified.

[PDF review copy](source_address_study.pdf) · [Method fragment](source_methods.tex) · [Result fragment](source_results.tex) · [Saved experiment](../research/coldcard/source_membership_baseline_20261102_162335/README.md) · [Evidence alignment](../ALIGNMENT.md)

## Article integration

Add `article_preamble.tex` once before `\begin{document}`. Place `\input{source_methods}` in `Our Work`, alongside the initial dataset description, and `\input{source_results}` in `Results`. The source-address sections supplement the financial/transaction work; their membership scores must not replace or be combined with transaction-target metrics. Reconcile the existing introduction's proposed GNN with this completed tabular baseline rather than asserting that GNN training occurred. The standalone `report.tex` is a review wrapper, not a replacement for the article or its author list/bibliography.

The fragments require only the listed standard LaTeX packages in addition to the original `graphicx` and `hyperref`. Exact observations are generated from the pinned saved JSON. Public reconstruction attribution and artifact links follow the text; no private raw cache or imported bulk address list is published.

## Source-address dataset and evaluation

### Observation unit and evidence

The observation unit is one unique decoded Bitcoin input source address with one fixed reference payment. The case cohort comprises 500 addresses whose payments entered the reported Coldcard collector in blocks 960188-960191 on 30 July 2026 UTC. Five later registry sources are kept outside this study. An address is neither a verified individual, a device nor an independent incident.

The target is `known_coldcard_core_membership`: 1 for these 500 fixed core sources and 0 for the selected sources outside the core and other case exclusions. The latter are operational comparisons, not certified legitimate or non-hardware addresses. All independently verified compromise and signing-device labels remain unknown. One exactly mapped owner report is retained as reported evidence, separate from verified labels. [SomaxBT's reconstruction](https://github.com/somaxbt/coldcard-drain-addresses/tree/1e7fef87060808c29beaf9d137eb5ff9e37f8811) and [Alvaro P.'s reconstruction](https://github.com/alva-p/coldcard-weak-rng-research/tree/f93cfed16302bb91c8409fdee9ce5576a34b7e52) corroborate all 500 source/payment relations. They observe the same chain and do not provide 500 independent owner confirmations. Their exact pinned files and attribution caveats remain in the repository's corroboration record.

### Acquisition, sampling and coverage

The source registry reuses the supplied transaction corpus. The same-block comparison census uses four complete, height/hash-anchored Blockchain.info block responses collected on 30 October. The census contains 5,526 distinct source addresses before exclusions and 5,025 eligible comparisons. A deterministic salted hash ranking selects 1,000 sources, with a two-comparisons-per-case quota in each reference-block stratum. No source is replaced after a collection failure or incomplete history. The census, selection and normalized evidence are public; private raw caches are not redistributed.

Address histories use the recorded Blockstream Esplora API route. Full-history pagination/counter audits and, where necessary, the separately validated anchored pre-cutoff collector support the published prefixes. That anchored method matched both prefixes and all fourteen variables for eight complete-history pilot controls across the four blocks. Successful saved pages were reused only after fingerprint and cursor-sequence checks. Provider reconciliation is not cryptographic inclusion verification. This report performs no new provider requests.

Exactly 1,378 vectors are available: 500 cases and 878 comparisons. The 122 remaining comparison prefixes are bounded-incomplete, with null vectors and no model score. They are retained in the selected population but excluded from fitting and scoring. Full-current-history coverage is a different measure: 864 comparison histories are complete and 136 incomplete. Fourteen of those incomplete current histories nevertheless have an exhausted, validated prior prefix.

| Reference block | Case available / selected | Comparison available / selected | Comparison unavailable |
| --- | --- | --- | --- |
| 960188 | 63 / 63 | 108 / 126 | 18 |
| 960189 | 110 / 110 | 179 / 220 | 41 |
| 960190 | 168 / 168 | 300 / 336 | 36 |
| 960191 | 159 / 159 | 291 / 318 | 27 |

### Predictor boundary and definitions

For a reference at height h, only confirmed transactions with height strictly less than h enter a feature. The whole reference block and all future data are excluded. This uses block heights, not timestamps or within-block transaction order. Reference-payment inputs, values, fees, recipients and UTXO-depletion outcomes remain outside the predictors, as do raw/hash identifiers, labels, collection counters and evidence metadata.

| Predictor | Definition and unit |
| --- | --- |
| `confirmed_tx_count` | Distinct confirmed prior transactions affecting the address; count. |
| `receipt_tx_count` | Prior transactions creating an output to the address; count. |
| `spending_tx_count` | Prior transactions consuming an address output; count. |
| `received_output_count` | Prior outputs received by the address; count. |
| `spent_output_count` | Address outputs consumed before cutoff; count. |
| `received_sat` | Sum of received prior-output values; integer satoshis. |
| `spent_sat` | Sum of consumed prior-output values; integer satoshis. |
| `balance_sat` | Received minus spent values before cutoff; integer satoshis. |
| `unspent_output_count` | Received outputs not yet consumed before cutoff; count. |
| `active_block_count` | Distinct prior heights containing address activity; count. |
| `activity_span_blocks` | Last minus first prior activity height; blocks; undefined for an empty prefix. |
| `blocks_since_first_activity` | Reference minus first prior activity height; blocks; undefined for an empty prefix. |
| `blocks_since_last_activity` | Reference minus last prior activity height; blocks; undefined for an empty prefix. |
| `median_spending_tx_fee_rate_sat_vb` | Median whole-transaction fee / virtual size for prior spending; sat/vB; undefined without spending. |

One transaction can be both a receipt and a spend. Undefined historical fee rates stay missing; they are not zero, the reference-payment fee, or an allocated fee for one address. Amounts are address-associated output values, not a certified stolen total. The saved audit reproduced every available vector from 35,323 normalized address/transaction observations.

### Frozen grouping and model

Connected components combine repeated source-address hashes, shared prior-transaction references, common reference TXIDs and identical fourteen-variable vectors including missingness. These 918 observed-link components are overlap safeguards, not proven ownership groups. Unknown prior links through the 122 excluded histories are not claimed absent.

Each component uses the lexical minimum address SHA256. SHA256 of the fixed prefix `coldcard-source-split-v1:42:` followed by that minimum hash determines a residue modulo ten: 0-6 for training, 7 for validation and 8-9 for test. Every partition has at least 20 rows of each membership class, with no measured component/shared-link group crossing partitions. No seed reroll or component splitting is used.

| Partition | Cases | Comparisons | Components |
| --- | --- | --- | --- |
| Train | 346 | 687 | 633 |
| Validation | 56 | 55 | 99 |
| Test | 98 | 136 | 186 |

One prespecified `DecisionTreeClassifier` is fitted on 1,033 training rows: Gini criterion, maximum depth 3, minimum 20 rows per leaf, balanced training class weights and random seed 42. Each of the fourteen original variables uses its observed training median; zero is a fallback only for an entirely missing training column. Fourteen fixed missingness indicators accompany the variables. Validation/test rows do not fit this preparation, select features/parameters/thresholds or enter a final all-row refit.

The exported score is a class-balanced training leaf proportion. Its field is `case_membership_score`. The membership decision includes every score >= 0.5. The three prespecified comparators are constant training membership prevalence, descending prior inactivity and descending prior balance. Undefined comparator values use the same training-only median fill. Comparators have ranking metrics only.

## Source-membership results and limitations

### Fixed development performance

In the frozen 234-address test partition, the tree recovers 97 of 98 core memberships and assigns one of 136 outside-core comparisons to the core class. Membership precision, recall and F1 are each 0.989796. These metrics evaluate the operational membership labels, not independently verified theft or hardware identity.

| Partition | AP | ROC-AUC | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- |
| Validation | 0.981534 | 0.990422 | 0.982456 | 1.000000 | 0.991150 |
| Test | 0.993757 | 0.994748 | 0.989796 | 0.989796 | 0.989796 |

| Partition | TP | FP | FN | TN |
| --- | --- | --- | --- | --- |
| Train | 346 | 6 | 0 | 681 |
| Validation | 56 | 1 | 0 | 54 |
| Test | 97 | 1 | 1 | 135 |

Train counts are resubstitution diagnostics. Validation and test are held out from fitting, but belong to the same previously inspected incident/window; they are not an untouched or independent-incident evaluation. All AP and ROC-AUC values were independently checked from tied score groups and pairwise ranking counts. Confusion counts and F1 also reproduce directly from the saved predictions.

| Fixed test method | Membership AP | Membership ROC-AUC |
| --- | --- | --- |
| Training-prevalence constant | 0.418803 | 0.500000 |
| Longer inactivity | 0.982880 | 0.986645 |
| Larger balance | 0.765014 | 0.911877 |
| Prespecified tree | 0.993757 | 0.994748 |

Inactivity alone already achieves test AP 0.982880. The tree's descriptive gain is 1.09 percentage points on this fixed partition. No independent significance or causal claim follows, and no additional parameter search or model was fitted after inspecting these results.

### Rules and errors

The fitted tree has five leaves and uses only prior balance and inactivity. At the fixed decision threshold, the positive-membership region requires float32-converted balance greater than 14,820,511.5 satoshis and inactivity greater than 1,006.5 blocks. A further split at 8,750 blocks distinguishes two positive leaf scores. This is the fitted cohort rule, not a proposed operational theft/device threshold. A redundant split between two zero-score comparison leaves is retained without post-hoc pruning. Exact replay conditions and per-partition node/leaf supports remain in the saved model and rules.

No explicit missingness indicator was selected, and no observed source reached a numeric split using an imputed value for that split variable. The full training-only preparation remains exported. This observation does not characterize the unknown vectors of excluded histories.

| Partition / membership error | Source ID | Prior balance (sat) | Inactivity (blocks) |
| --- | --- | --- | --- |
| validation / FP | `comparison_0328` | 16604900 | 145611 |
| test / FN | `cohort_0191` | 69145962 | 409 |
| test / FP | `comparison_0401` | 40096077 | 7000 |

The missed case source `cohort_0191` has 105 earlier receipt transactions and last activity only 409 blocks before reference. It falls outside the learned inactivity region despite its case membership. The test comparison `comparison_0401` has one earlier receipt, a balance of 40,096,077 satoshis and 7,000 blocks of inactivity, resembling the covered case profile. The validation error is also an old-funded comparison. These are membership errors; neither predictions nor corrections settle compromise or device status.

### Coverage and inference limits

Coverage is 100% for cases and 87.8% for selected comparisons, ranging from 81.36% to 91.51% across comparison strata. The sampled core prevalence increases from 33.33% of selections to 36.28% of available vectors. The 122 unavailable comparisons have median saved full-current-history transaction count 3,347, versus 3 for available comparisons. These counts were observed at different collection snapshots and are diagnostic metadata, never prior-block predictors or estimates of missing features. Missingness cannot be assumed random.

All 500 positives come from one retrospectively reconstructed incident. Core membership and case evidence were learned after the event; their publication/availability dates are not established for prospective use. Addresses are not independent victims or devices. Same-chain reconstruction agreement, an owner report, provider coverage and genuine device/compromise verification are distinct evidence tiers. Independently verified compromise/device labels remain unknown for every selection, and comparisons are not verified benign examples.

The result supports a reproducible, interpretable description of covered source profiles and a narrow within-window membership baseline. It does not establish a cause of loss, a signing-device fingerprint, calibrated theft probabilities, independent-incident transfer or general blockchain detection performance. The selection prevalence is study-defined. The 122 bounded-incomplete prefixes remain unresolved; a validated prefix also does not certify a complete current history. The frozen external nineteen-feature forest and all earlier experiment artifacts remain unchanged.

### Reproducibility and supported conclusion

The fitted experiment is pinned to [commit 00659df](https://github.com/HnsHugo/STAGE-UFU/commit/00659df35d3140143fa12b37ba35ea56722a4854) on branch `task-2-wallet-analysis`. Its protocol freezes the data, component assignments, preparation, tree parameters, threshold and software versions. All 1,378 JSON-exported scores exactly match the fitted estimator. Thirty focused tests and verification without a model refit passed in the saved execution. The report builder checks the saved predictions, confusion counts, F1, fingerprints, exclusions and component partitioning; it performs no new training or collection.

A separate independent evaluation would require a justified additional incident/source universe, evidence-backed label definitions and a new prespecified protocol. The current validation/test outcomes must not be reused for tuning or described as newly independent evidence.

## Sources and saved evidence

- [Case-source consolidation and evidence tiers](../research/coldcard/source_dataset_20261030/README.md).
- [Two published reconstruction comparisons and pinned sources](../research/coldcard/source_corroboration_20261030/README.md).
- [One owner-report adjudication](../research/coldcard/owner_report_adjudication_20261030/README.md).
- [Fixed same-block comparison selection](../research/coldcard/source_comparison_selection_20261030/README.md).
- [Coverage/grouping audit](../research/coldcard/source_comparison_feasibility_20261102_1603/README.md).
- [Frozen fitted experiment and scores](../research/coldcard/source_membership_baseline_20261102_162335/README.md).
- [Public normalized predictor view](../research/coldcard/reference_tail_continuation_20261102_1508/precutoff_feature_view.json.gz).
- [Report input/output provenance](provenance.json).

SomaxBT's pinned `coldcard-drain-addresses` reconstruction and Alvaro P.'s pinned `coldcard-weak-rng-research` reconstruction corroborate chain observations, not independent owner/device ground truth. Exact URLs, versions, licensing caveats and the limited input-value comparison are retained in the linked corroboration review. No external CSV is copied into this report.

## Check and compile

From the repository root:

```sh
python "Task 2/docs/build_source_address_study.py" check
cd "Task 2/source_address_study"
mkdir -p /tmp/ufu-report-build
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/ufu-report-build report.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/ufu-report-build report.tex
```

Relative fragment inputs resolve from this working directory. The two passes settle long-table widths and references. The checked PDF is already included. Report checks read frozen results and never fit a model or query a provider.
