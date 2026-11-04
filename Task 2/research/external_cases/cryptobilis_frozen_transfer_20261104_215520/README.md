# Frozen Coldcard model on CryptoBilis source membership

Completed 4 November 2026 UTC. This prespecified inference unit applies the existing Coldcard JSON tree to the exact previously published external eligibility set. The target is `cryptobilis_reference_source_membership`: an input source linked to a pinned reference payment in the historical CryptoBilis case. The original model target is `known_coldcard_core_membership`; this is an explicit exploratory proxy-transport hypothesis. Source-level theft, seed origin and signing-device labels remain unknown.

## Main result

The frozen model's external membership F1 is **0.629834**, precision **0.966102**, recall **0.467213**, AP **0.688142** and ROC-AUC **0.727151**. It retrieves 57 of 122 case sources, misses 65, and classifies two comparisons as positive. The fixed inactivity and balance rankings both outperform its AP and ROC-AUC on this eligible sample. No threshold, parameter, feature or model was changed in response.

| Prespecified method | Membership AP | Membership ROC-AUC | Membership F1 at >=0.5 |
| --- | ---: | ---: | ---: |
| Frozen Coldcard tree | 0.688142 | 0.727151 | 0.629834 |
| Descending prior inactivity | 0.854026 | 0.950016 | Not defined; ranking only |
| Descending prior balance | 0.763244 | 0.845387 | Not defined; ranking only |
| Constant Coldcard-training prevalence | 0.443636 | 0.500000 | Not defined; ranking only |

The constant score is 346/1033 = 0.334947, fixed from Coldcard training membership. Its AP equals the external sampled prevalence, 122/275 = 0.443636; this is not an external imputation or recalibration. The univariate comparators use the same saved Coldcard-training fills and float64 rankings, without a fitted classification threshold.

| Observed external proxy class | Predicted positive | Predicted negative | Total |
| --- | ---: | ---: | ---: |
| Linked case source | 57 | 65 | 122 |
| Unattributed comparison | 2 | 151 | 153 |
| Total | 59 | 216 | 275 |

The error names refer only to this graph-membership proxy. A comparison is not a certified legitimate, uncompromised or non-hardware address. Every one of the 67 membership errors is preserved with its original fourteen variables, label tier, reference hash, component, leaf and path in [errors.json.gz](errors.json.gz).

## Fixed population and attrition

| External population | Case sources | Comparisons | Total |
| --- | ---: | ---: | ---: |
| Original fixed selection | 122 | 244 | 366 |
| Available complete prior-prefix vectors | 122 | 207 | 329 |
| Complete vectors quarantined for measured development overlap | 0 | 54 | 54 |
| Bounded-incomplete prefixes without vectors | 0 | 37 | 37 |
| Exact eligible population scored | 122 | 153 | 275 |

All 366 original selections are retained in [scoring_manifest.json.gz](scoring_manifest.json.gz). The 54 quarantined vectors and 37 unavailable prefixes have null scores; no excluded source was scored, imputed as a complete prefix, replaced or recollected. Case prevalence is 33.33% in the fixed selection, 37.08% among complete vectors and 44.36% in the scored cohort. These are complete-case/quarantine results, not unbiased performance for every selected address or blockchain prevalence.

The [prior overlap audit](../cryptobilis_overlap_20261104_205032/README.md) and its exact manifest remain unchanged. The whole CryptoBilis incident stays outside fitting. The four measured cross-development components, the original 918 Coldcard groups, all training/validation/test assignments and both data views are preserved. Missing links of 122 bounded Coldcard prefixes and 37 bounded external prefixes are unknown, so measured-link quarantine does not prove entity independence.

## Observed fixed-rule errors

The exported root tests prior `balance_sat`, converted to float32, against 14,820,511.5 sat (about 0.148205 BTC). Its low-balance branch contained zero case sources and 642 comparisons in the original Coldcard training export. In CryptoBilis it contains 63 case sources and 137 comparisons. All 63 case sources in that branch become false negatives under the unchanged tree. Two additional false negatives have higher balances but enter the fixed `blocks_since_last_activity <= 1006.5` branch.

| Frozen leaf | Exported Coldcard membership score | External cases | External comparisons | False negatives | False positives |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2 | 0.000000 | 0 | 3 | 0 | 0 |
| 3 | 0.000000 | 63 | 134 | 63 | 0 |
| 5 | 0.000000 | 2 | 14 | 2 | 0 |
| 7 | 0.888171 | 27 | 1 | 0 | 1 |
| 8 | 0.996957 | 30 | 1 | 0 | 1 |

Both split variables are observed for all 275 scored sources. Spending fee rate is undefined for 121 case sources and 101 comparisons; its frozen fill/indicator is retained, but that column and its indicator do not occur in the exported tree's splits. The observed errors therefore reproduce through the actual balance/inactivity branches; they are not a preprocessing mismatch. This diagnosis describes the fixed rule on these samples and does not select a replacement threshold or prove a general cause of incident differences.

The previously inspected Coldcard internal test F1 remains 0.989796 (97 TP / 135 TN / 1 FP / 1 FN). It uses a different source-membership target/population within the original incident. The external result shows that the strong internal score does not establish reliable transport to the specified CryptoBilis proxy. It does not justify refitting on the now inspected external labels.

## Descriptive block results

| Reference block | Cases / comparisons scored | Tree precision | Tree recall | Tree F1 | Tree AP | Inactivity AP |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 970590 | 111 / 135 | 0.964912 | 0.495495 | 0.654762 | 0.706517 | 0.847673 |
| 970591 | 11 / 18 | 1.000000 | 0.181818 | 0.307692 | 0.492163 | 0.992424 |

These are descriptive strata of one inspected incident, not independent replications or separate minimum-20 feasibility claims. No threshold was fitted for either block. No address-level resampling interval is presented as incident-level generalization evidence.

## Method, validation and interpretation

The [protocol](protocol.json) and implementation were [published before the first external scores](https://github.com/HnsHugo/STAGE-UFU/commit/719067dd4467bd59d7da6004cacad022fb5aaf68). All 154 input pins verify. The standard-library evaluator uses exactly the fourteen allowed prior-block values, the exported training medians, fourteen fixed missing indicators, float32 tree inputs, `<=` left branching and the original `>=0.5` decision. No identifier, event outcome, full-current counter, label or reference-block metadata enters prediction. All underlying normalized histories remain strictly before each frozen reference block.

Twenty failure-oriented tests pass, including float32 routing, ties, fixed-threshold equality, cyclic trees, median/indicator preservation, exclusion guards and label/full-history promotion failures. The [independent verifier](independent_verification.json) replays every one of the 275 scores, paths, missingness patterns and comparator values through the preserved NumPy implementation. Scikit-learn independently agrees with all twelve overall/block/method metric sets. Every error and all node supports verify. Estimator `.fit` and preprocessing fitting are explicitly blocked during this check. Python 3.12.14, NumPy 2.3.5 and scikit-learn 1.8.0 match the recorded runtime.

This unit performs zero new model fits, preprocessing fits, threshold searches, provider requests, replacements or new splits. The old model and scientific outputs are unchanged. Scores are class-balanced Coldcard leaf proportions, not calibrated theft/device probabilities. Individual current source histories remain not collected/reconciled by this prefix protocol; the separate Coldcard full-history statuses are preserved. Both collector examples belong to one historical external incident, already inspected before this evaluation. This result supports a limited structural-proxy comparison, with explicit coverage, selection and entity-independence limits.

The next aligned unit is the scientific write-up of this completed frozen transfer and its negative transport result, with the error-path and comparator evidence integrated into the article. Any later ML adaptation requires a separately specified development/evaluation design and independent evidence; keep the inspected CryptoBilis result and all old thresholds frozen.

## Reproduction and files

Use [predictions](predictions.json.gz), [full metrics](summary.json), [primary reconstruction fingerprints](verification.json), [independent verification](independent_verification.json) and the [completion checkpoint](resume_checkpoint.json). Public normalized evidence suffices; no raw private caches or provider access is needed.

```sh
python "Task 2/research/external_cases/evaluate_cryptobilis_frozen.py" verify "Task 2/research/external_cases/cryptobilis_frozen_transfer_20261104_215520/protocol.json"
python "Task 2/research/external_cases/verify_cryptobilis_frozen_independently.py" verify "Task 2/research/external_cases/cryptobilis_frozen_transfer_20261104_215520/protocol.json"
python -m unittest discover -s "Task 2/research/external_cases" -p "test_cryptobilis_frozen.py"
```
