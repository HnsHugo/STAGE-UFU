# Descriptive external scoring pilot — 14 October 2026

The fixed 19-base-feature forest is fitted solely on the original 52736 Real-CATS training addresses. It uses 100 trees, depth 20, minimum leaf size 20, sqrt feature sampling, equal class weights, seed 42 and training-only median imputation with two missingness indicators. The development threshold remains strictly score > 0.15. No external address or label enters fitting. No validation/test prediction or hyperparameter search occurs in this scoring step.

The extractor uses complete saved confirmed histories: EFF collected on October 14 and the two BTCPay collectors on October 13. It rechecks stable provider counters, pagination exhaustion, distinct transaction identities and monetary sums through the common history audit. It rejects addresses overlapping either full Real-CATS file, duplicate external addresses and schema mismatches. Feature order is identical to training. Histories and their file hashes are retained in the report. The original 22-feature forest is not scored externally.

| Address role | Address | Source-category score | Above fixed 0.15 threshold |
|---|---|---:|---|
| Official EFF donation recipient | 3LTu6uavQ4A3kgDauZipyGqcHQEUSVe2so | 0.045173 | No |
| BTCPay collector A, operator testimony plus reconciled transaction | 19jSfadPiKa4aCefj4F7uEYbhMEt2L8SCH | 0.271938 | Yes |
| BTCPay collector B, research attribution | 17C7EZC1VTrXzSQneiaJv2W6tQh1vCRSnF | 0.210626 | Yes |

Scores are not calibrated probabilities of theft or illegality. The flag only means the forest's Hack/Theft source-category score exceeds its previously selected development threshold. These outcomes are consistent with the documented address purposes/attributions, but none is scored against independently established binary ground truth. Do not report accuracy, precision, recall or a confusion matrix for this three-address pilot.

No numerical feature falls outside the training minimum/maximum for these observations. This coarse range check does not establish multivariate distribution similarity, temporal compatibility or model reliability. Nineteen extraction conventions were reconciled on seven development training addresses; all edge cases are not certified. Three unreconciled variance fields are omitted from both training and extraction.

There is one donation entity and one conservative reported theft case with two addresses, not three independent cases. Exact address non-overlap does not exclude shared ownership, counterparty overlap or selection bias. EFF's official donation publication supports its purpose, not legitimacy of every receipt. Collector A has direct public operator testimony; B has weaker research attribution. The source_record retained inside older saved histories reflects collection-time evidence; the updated confidence review is in ../../research/external_cases/EXTERNAL_EVIDENCE_REVIEW.md and is not a training label.

The observation policy is full history at collection time, including later spending. It is not the 24-hour decision-time snapshot and does not demonstrate early detection or discovery of previously unknown criminal addresses. Historical labels and observations have different availability dates. Source categories and evidence labels differ from the intended verified stolen-fund recipient target.

## Reproduction

```bash
python score_external_histories.py /path/to/Real-CATS new_external_scores.json \
  ../../research/external_cases/eff_history_20261014/3LTu6uavQ4A3kgDauZipyGqcHQEUSVe2so.json.gz \
  ../../research/external_cases/pilot_histories_20261013/19jSfadPiKa4aCefj4F7uEYbhMEt2L8SCH.json \
  ../../research/external_cases/pilot_histories_20261013/17C7EZC1VTrXzSQneiaJv2W6tQh1vCRSnF.json
```

The output stores all 19 feature values, missing-value lists, training range checks, observation provenance and scores. Three benchmark and six theft-case tests pass. Source checksums and complete-history reconciliation passed on the real scoring inputs. The next useful step is to expand independent documented comparison entities and theft cases under one predefined observation/label policy before making performance claims.
