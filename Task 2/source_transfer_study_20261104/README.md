# Frozen source-membership transfer supplement

English article-ready supplement to the preserved [Coldcard source-address study](../source_address_study/README.md). It reports the completed CryptoBilis transfer and its negative transport result, without fitting or recomputing model scores.

[PDF review copy](source_transfer_study.pdf) · [Our Work fragment](transfer_methods.tex) · [Results fragment](transfer_results.tex) · [Saved experiment](../research/external_cases/cryptobilis_frozen_transfer_20261104_215520/README.md)

## Article integration

Retain the original article and the two earlier Coldcard fragments. Add `transfer_methods.tex` under `Our Work`, after the source dataset/baseline description, and `transfer_results.tex` under `Results`, after the fixed Coldcard results. The `transfer_preamble.tex` packages match the earlier supplement: use those packages only once, with the article's existing `hyperref`. The wrapper `report.tex` is a standalone review copy and does not replace the main article, author list or bibliography. No live Overleaf document or originally supplied article file was edited.

For an uploaded folder named `source_transfer_study_20261104`, the additions are:

```tex
% Preamble: skip this input if these packages were already added for the Coldcard supplement.
\input{source_transfer_study_20261104/transfer_preamble}
% Inside Our Work, after the earlier source_methods:
\input{source_transfer_study_20261104/transfer_methods}
% Inside Results, after the earlier source_results:
\input{source_transfer_study_20261104/transfer_results}
```

The existing introduction should distinguish the completed tabular baseline and proxy transfer from proposed GNN work. The conclusion should report the limited transport and stronger inactivity ranking, without claiming verified theft/device identification. [ARTICLE_MAP](../docs/ARTICLE_MAP.md) tracks the supplied outline. [Provenance](provenance.json) records saved sources and generated-text hashes; [facts](tables.json) retain exact values.

## External source dataset and fixed protocol

### Question, observation unit and evidence

We asked whether a frozen model of Coldcard source membership transports to an explicitly defined source-linkage proxy in a second historical incident. One observation is one decoded Bitcoin input source address with a fixed reference payment. Membership identifies a relation to the selected case corpus; it does not verify a victim, signing device or seed origin. The original target, `known_coldcard_core_membership`, and external target, `cryptobilis_reference_source_membership`, remain separate operational definitions.

The Coldcard development study retains 500 core sources and 1,000 fixed same-block comparisons. It provides 1,378 complete prior-prefix vectors (500 cases, 878 comparisons); 122 incomplete comparisons remain unscored. Its 918 measured-link components yielded fixed training/validation/test supports of 1,033/111/234 addresses. The original one-incident fitted result is preserved, rather than retrained with external examples.

For the historically attributed CryptoBilis collectors, the pinned snapshots identify 122 source candidates in 122 reference payments, with 140 input-outpoint observations. Their reference blocks are 970590 and 970591, in the fixed UTC day of 9 October 2026. All source-level independently verified compromise, signing-device and seed-origin labels remain unknown. The historical attribution could not be refreshed in the earlier source review; it is not upgraded here. Both collectors belong to the same external incident.

### Acquisition, deterministic comparisons and attrition

The two height/hash-anchored complete blocks contain 7,944 transactions and 9,356 distinct decoded positive input sources. A frozen salted hash ranking selects 244 comparisons, with block quotas 222 and 22. Exclusions include all 1,500 development addresses and the prespecified case/source/collector exclusions. Reference assignment uses the first occurrence by block height and lexical TXID. No collection failure, vector, fee or score changes the sample or triggers replacement.

The anchored prior-prefix collector reuses the recorded Blockstream Esplora route, checks reference block/hash and input value/count, funding closure, reverse-height order and an empty terminal page. Its original pilot matched prefixes and all fourteen variables for eight complete-history controls. Four bounded passes finalized all 366 external selections: 329 complete vectors and 37 retained bounded-incomplete comparisons. Across the passes, 2,262 saved/reused response fingerprints and 19 batch snapshots were verified. Provider-indexed prefix reconciliation does not establish cryptographic inclusion or a complete current address history. This supplement requests no provider data.

| Stage | Case sources | Comparisons | Total |
| --- | --- | --- | --- |
| Fixed selection | 122 | 244 | 366 |
| Complete prior-prefix vectors | 122 | 207 | 329 |
| Complete vectors quarantined | 0 | 54 | 54 |
| Bounded prefixes, no vector | 0 | 37 | 37 |
| Scored cohort | 122 | 153 | 275 |

Case prevalence rises from 122/366 (33.33%) in the original selection, to 122/329 (37.08%) among complete vectors and 122/275 (44.36%) in the scored cohort. The 54 quarantined complete vectors and 37 incomplete prefixes stay in the saved selection with null scores. These are conditional complete-case/quarantine results, not unbiased estimates for all selected sources.

### Cutoff, overlap and unchanged model

Every predictor uses only confirmed transaction heights strictly below its own frozen reference height. The entire reference block and future are excluded. The unchanged fourteen variables measure receipt/spending transaction and output counts, received/spent/balance values in satoshis, unspent outputs, active blocks, activity span, age/inactivity and median prior-spending fee rate. Reference-payment outcomes, identifiers, labels, provider counters and evidence metadata are excluded from model inputs.

All 1,866 development/external identities and all available normalized prefixes enter the overlap audit. Links comprise repeated address hashes, common prior transactions, common reference payments and exact complete-vector equality including missingness. A conservative transaction-role guard also checks a prior reference in one dataset against an event reference in the other. Forty-five shared prior-transaction groups and one identical-vector group generate four components spanning both datasets. All their external members are quarantined: 67 comparisons, of which 54 have vectors and 13 are already incomplete. Transitive closure matters; quarantine is not restricted to directly matching addresses. Independent graph reconstructions agree, and the original development groups and partitions are unchanged.

Exactly 122 cases and 153 comparisons remain eligible. This passes the frozen overall minimum of 20 per class, without asserting that each block meets that support. All external observations remain outside fitting. Missing links of 122 incomplete Coldcard prefixes and 37 incomplete external prefixes are unknown; measured-link quarantine is not proof of entity independence.

The existing Gini decision tree retains maximum depth 3, minimum 20 samples per leaf, balanced training class weights and seed 42. Fourteen numeric values use only the original training medians, with fourteen fixed missing indicators. The exported JSON tree receives float32 inputs and keeps its original score decision of at least 0.5. Its class-balanced training leaf proportions are not calibrated theft/device probabilities. No model/preprocessing fit, feature search, new split, calibration or threshold change is performed.

### Prespecified comparisons and reproducibility

The comparators are constant Coldcard-training membership prevalence (346/1,033), descending prior inactivity and descending prior balance. The latter use the same training-only median fills, in float64; they have ranking metrics only. We report AP and ROC-AUC for all methods and precision, recall, F1 and confusion counts for the tree at its unchanged threshold. Block results are descriptive strata of one incident.

The protocol and both implementations were published before the first external scores. A standard-library tree traversal and the preserved NumPy implementation agree exactly on all 275 float32 scores, paths and missingness patterns. Scikit-learn independently agrees with all twelve overall/block/method metric sets. All 67 errors, node supports and 91 exclusions are verified; fitting paths are blocked during verification. Twenty failure-oriented tests pass. This write-up reads those saved results without inference, fitting or collection.

## External results and interpretation

### Frozen transfer performance

On the 275 eligible external addresses, the frozen tree attains membership precision 0.966102, recall 0.467213 and F1 0.629834. It recovers 57 of 122 case sources, misses 65 and assigns two of 153 comparisons to the case class. AP is 0.688142 and ROC-AUC is 0.727151.

| Method | AP | ROC-AUC | F1 |
| --- | --- | --- | --- |
| Frozen tree | 0.688142 | 0.727151 | 0.629834 |
| Prior inactivity | 0.854026 | 0.950016 | Ranking only |
| Prior balance | 0.763244 | 0.845387 | Ranking only |
| Training-prevalence constant | 0.443636 | 0.500000 | Ranking only |

| External proxy class | Predicted positive | Predicted negative |
| --- | --- | --- |
| Case source | 57 | 65 |
| Comparison | 2 | 151 |

The fixed inactivity ranking has higher AP and ROC-AUC than the tree, as does the balance ranking. No classification threshold was fitted for either comparator, so their AP values are not comparator F1 scores. The constant's score remains the training prevalence 0.334947; its external AP equals the scored prevalence 0.443636, with ROC-AUC 0.5. This is a ranking property of a constant, not external recalibration.

The preserved Coldcard internal test F1 is 0.989796 (97 TP, 135 TN, one FP and one FN). The external experiment uses a different source-membership target and a selected population in another incident. It therefore does not measure the same estimand, but demonstrates that the strong internal separation does not ensure reliable transport under the specified external proxy. No threshold was changed to improve this observed result.

| Reference block | Cases / comparisons | Tree F1 | Tree AP | Inactivity AP |
| --- | --- | --- | --- | --- |
| 970590 | 111 / 135 | 0.654762 | 0.706517 | 0.847673 |
| 970591 | 11 / 18 | 0.307692 | 0.492163 | 0.992424 |

The second block has only eleven case sources and eighteen comparisons. These stratum summaries are not independent replications, significance tests or separate minimum-20 claims. The incident, entity dependence and selection limits remain present even where a univariate ranking is high.

### Fixed-rule error diagnosis

The root tests float32-converted prior balance against 14,820,511.5 satoshis (about 0.148205 BTC). Its lower-balance branch contained zero case sources and 642 comparisons in the Coldcard training export. In CryptoBilis, 63 case sources and 137 comparisons enter this branch. All 63 case sources become false negatives under the unchanged rule. The two remaining false negatives have higher balances but enter the fixed inactivity-at-most-1,006.5-block branch. This is an exact replay explanation, not a newly selected threshold or a causal account of incident differences.

| Leaf | Frozen score | Cases | Comparisons | FN | FP |
| --- | --- | --- | --- | --- | --- |
| 2 | 0.000000 | 0 | 3 | 0 | 0 |
| 3 | 0.000000 | 63 | 134 | 63 | 0 |
| 5 | 0.000000 | 2 | 14 | 2 | 0 |
| 7 | 0.888171 | 27 | 1 | 0 | 1 |
| 8 | 0.996957 | 30 | 1 | 0 | 1 |

Both numeric split variables are observed for every scored address. Prior-spending fee rate is undefined for 121 cases and 101 comparisons; its saved median/indicator is preserved, but neither appears in a tree split. The observed errors reproduce through the fixed balance/inactivity conditions rather than a preparation mismatch. All 67 errors retain their source ID, original fourteen values, label tier, reference hash, component, score and path in the machine-readable export.

### Limits and supported conclusion

The operational positive label is linkage to a selected historical collector payment, not independently verified loss or hardware use. Comparisons are unattributed outside-reference sources, not certified legitimate or non-hardware examples. Both collector snapshots belong to one already inspected incident. Neither the address count nor measured-link grouping establishes independent victims, devices or entities; no untouched or prospective test is claimed.

Coverage and quarantine change the evaluation population and class prevalence. Incomplete prefixes have no vector, while an exhausted prior prefix does not certify an entire current history. Individual CryptoBilis full-current-history status remains not collected for this source. The separate Coldcard comparison full-history counts (864 complete, 136 incomplete) are unchanged. Provider reconciliation, cryptographic inclusion, source attribution and owner/device evidence are distinct claims.

The results support a reproducible, limited comparison of source-linkage profiles. They expose a failure of reliable frozen-tree transport and show that a prespecified inactivity ranking can outperform that model in this selected sample. They do not validate theft probabilities, hardware-wallet identification or population-wide generalization. The high inactivity AP also does not turn inactivity into a validated theft detector. Preserving the negative transfer result is scientifically necessary; adapting the tree or its threshold to these inspected answers would require a separately specified design and independent evaluation evidence.

## Saved sources and reproduction

- [Historical source evidence and attribution limits](../research/external_cases/cryptobilis_source_readiness_20261102/README.md).
- [Deterministic complete-block census and selection](../research/external_cases/cryptobilis_source_selection_20261103_002428/README.md).
- [Final bounded acquisition audit](../research/external_cases/cryptobilis_reference_prefix_20261104_201345/README.md).
- [Overlap, quarantine and eligibility](../research/external_cases/cryptobilis_overlap_20261104_205032/README.md).
- [Fixed model, all scores/errors and independent verification](../research/external_cases/cryptobilis_frozen_transfer_20261104_215520/README.md).
- [Original Coldcard fitted study](../research/coldcard/source_membership_baseline_20261102_162335/README.md).

The supplement's builder checks saved hashes, source selection, confusion/F1, errors, exclusions and branch counts. It imports no model library, evaluates no model and queries no provider. Render/compile records are in `validation.json`; the previous five-page Coldcard report is preserved separately.

```sh
python "Task 2/docs/build_source_transfer_study.py" check
```
