# Expanded training-only edge-case reconciliation

Four deterministic training references cover nonconstant allocated fees, no outgoing transactions, multiple own input slots, and receipt plus spending in the same transaction. Selection is by SHA256(address) within predefined source-profile strata, with 2–10 source transactions. All four selected addresses are source-labeled benign; this is schema coverage, not a balanced performance sample. One multiple-input reference was already collected, so these checks add three new unique addresses (seven unique training references overall), not four independent new examples.

All four current histories exhaust pagination and reconcile with stable provider counts. They contain 9, 10, 17 and 14 transactions. Restricting each to the end of its source last-time minute retains 6, 9, 6 and 10 respectively, excluding 3, 1, 11 and 4 newer transactions. Matching source profile totals supports that historical restriction. Date convention remains a development assumption, not a known original implementation detail.

## Result

Nineteen of 22 probes match every edge reference under the disclosed rounding tolerance. Three variance fields fail on nontrivial cases:

| Field | Matching edge references | Example expected | Example population variance |
|---|---:|---:|---:|
| transaction_fee_Variance | 2/4 | 11377.52083 | 429680.25 |
| received_Variance_BTC | 2/4 | 6276800247 | 7068007724.4 |
| sent_Variance_BTC | 1/4 | 20185933315 | 8295690640.1875 |

These example values refer to the nonconstant-fee address bc1q8xekklc4ul3vsufy804ecyxu563rac4ynd4rsh. Full per-address comparisons and sample-variance alternatives are in edge_reconciliation_20261014.json. Errors materially exceed rounding tolerance. The same-transaction receipt/spend reference also disagrees on all three variance fields. Sample variance does not explain those discrepancies.

The earlier statement that 21 of 22 features matched four references remains true for that limited sample; this expanded check demonstrates why zero-variance examples cannot certify the variance convention. The previous fee-variance agreement was explicitly marked unidentifiable. Revised external readiness therefore blocks all three variance fields, not only sent variance.

In these cases the equal-input-slot fee sum, direction counts, individual-slot monetary sums/extrema, activity-day mapping and counterparty multiplicity still reconcile. The no-spending example confirms missing sent extrema and zero spent totals/fee/variance under the source convention. Same-transaction receipt/spend contributes to both direction counts, while transaction_number counts each transaction once. Counters describe transaction participation, not proven ownership of external addresses. Seven development addresses cannot certify all edge cases or all source populations.

## Consequence for external evaluation

external_feature_contract_20261014.json records 19 matched columns and three unreconciled variances. It explicitly marks external scoring unavailable for the original 22-feature forest. Do not fabricate variances, omit columns only at prediction time, or call median substitution a valid extraction mapping.

A practical next experiment is to train and compare a separate 19-feature forest on training/validation only, leaving all three variances out in both domains. The original model remains a frozen offline reference. That alternative would still require broader extraction and case-label checks before population-level claims; EFF/BTCPay remain descriptive external cases. No model predictions or reserved-test extraction occurred in this step.

## Reproduction

```bash
python select_edge_references.py /path/to/Real-CATS new_edge_selection.json
python ../../research/external_cases/collect_pilot_histories.py new_edge_selection.json new_edge_history --max-pages 12
python reconcile_training_profiles.py /path/to/Real-CATS new_edge_report.json edge_references_20261014
```

Original source hashes and original training membership are enforced. Normalized saved histories preserve original retrieval hashes and reproduce the comparisons. Three benchmark and six theft-case tests pass. Provider consistency does not replace cryptographic inclusion verification.
