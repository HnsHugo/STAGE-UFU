# EFF history collection and feature compatibility

EFF is a documented donation comparison candidate, not verified benign ground truth. The fixed address and first-party source are retained in the selection. Archive and FSF remain selected but their histories are not collected in this step.

The original collector now accepts --max-pages (default 6, preserving earlier runs). With a 12-page limit EFF's confirmed history exhausts pagination and reconciles exactly with stable before/after provider counters: 191 distinct transactions, 97 funded slots and 97 spent slots, 1108591222 sats received and the same input value spent. There are 97 receiving and 94 spending transactions. Observations span 2024-08-30 18:00:42 UTC to 2026-10-14 06:29:09 UTC. The final balance is zero. Provider reconciliation is not independent cryptographic inclusion verification.

The equal-maturity snapshot ends exclusively at 2024-08-31 18:00:42 UTC, 24 hours after first confirmed receipt. Four earlier transactions include two receipts and two spends, 161067 sats each direction, with zero balance. Label availability at that time is unknown. Snapshot labels remain pending comparison-policy review.

The normalized complete history is gzip-compressed. Script bodies are omitted; address/value pairs, outpoints, fees, weights and block anchors remain. The manifest preserves original, compressed and decompressed hashes. Saved normalized transactions reproduce provider reconciliation and the original cutoff snapshot exactly.

## Compatibility decision

No model scores are produced. The 22-column Real-CATS model requires an adapter whose semantics have been validated against original profiles, not only matching column names.

| Feature family | Locally calculable quantities | Outstanding equivalence check |
|---|---|---|
| Flow/balance/counts | Received outputs, spent input value, remaining balance, receipt/spending transaction counts | Self-transfers and aggregation policy must match source |
| Time/activity | First/last confirmed times, lifetime seconds, UTC active/receipt/spending dates | Source day timezone convention |
| Slots | Count matching address input/output slots | Directly reconcilable with provider counters |
| Amount extrema/variance | Per-transaction own-input and own-output aggregates | Slot versus transaction aggregation, variance denominator, empty-direction policy |
| Fees/fee variance | Whole-transaction fees available | Multi-party transaction fee assignment and aggregation/variance convention |
| Counterparty counts | All input/output address observations retained | Occurrences versus unique addresses, direction mapping and self-exclusion |

The [primary Real-CATS paper](https://arxiv.org/html/2501.15553v1), Tables 1–2 and Section 3.2, specifies monetary values in satoshis, lifetime in seconds, and activity as counts of days. It describes Sent_counters as sender counts for receipt transactions despite its name; naming alone is unsafe. Variance denominator, fee allocation and all edge-case implementation details require further reconciliation. These ambiguities are material because fee and counterparty features carry substantial model importance.

The next adapter validation should use complete raw transaction records for addresses already in Real-CATS and compare all 22 extracted values against published rows. Fix conventions using training-only reference addresses. The current full-history EFF observation and the 24-hour snapshot are different feature domains; a cutoff-safe detector needs cutoff-safe training data too. A three-organization convenience cohort and one theft case cannot confirm population-level performance.

## Reproduction

```bash
python collect_pilot_histories.py eff_history_20261014/selection.json new_eff_history --max-pages 12
python describe_complete_history.py eff_history_20261014/3LTu6uavQ4A3kgDauZipyGqcHQEUSVe2so.json.gz new_description.json
python -m unittest discover -p 'test*.py'
```

Six existing theft-case tests pass; real-history counter reconciliation, gzip round trip, checksums and snapshot equality are also checked. No final-test predictions or model tuning occur.
