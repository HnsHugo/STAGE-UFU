# Training-only extraction convention probes

Four complete provider histories are reconciled against pinned Real-CATS profiles: two existing pilot addresses in the original training split and two new training references. New references are selected deterministically by SHA256(address), separately for benign and Theft, with 3–6 source transactions. The membership gate excludes validation/test addresses before feature extraction in this script. Two earlier pilot histories belong to the reserved test and were excluded from formula development. Their membership was discovered during inspection; no test prediction or performance tuning occurred.

One new address has 17 current transactions but only six at the original profile date. Reference transactions are restricted to strictly before the end of the last-time minute printed in the source row, interpreted as UTC. Eleven newer transactions are excluded. Counts, slots, monetary totals and lifetime then reconcile. This is a retrospective schema check, not a decision-time prediction window. A transaction after the source snapshot within that final minute would require a stricter cutoff; none of the observed count comparisons indicates such a discrepancy here.

Twenty-one of 22 feature probes match all four references at relative tolerance 0.005 and absolute tolerance 0.000001, accommodating source values rounded to roughly three significant figures. This tolerance is disclosed, not a claim of exact numerical equivalence. Detailed expected and extracted values are in schema_reconciliation_20261014.json.

| Convention | Evidence from training references | Remaining limit |
|---|---|---|
| Fees | Sum transaction fee multiplied by own input-slot count / total input count | Equal-slot allocation is a dataset convention, not actual economic fee responsibility |
| Activity | activity_w matches receipt-day count, activity_d spending-day count in the differentiating reference | Contradicts intuitive names and paper descriptions; needs broader training checks |
| Amount extrema | Individual own input/output slots | Larger self-transfer and repeated-slot cases need checks |
| Counterparties | sent_counters counts other input slots in receipts; received_counters counts other output slots per own input slot | Unaddressed scripts and mixed ownership remain edge cases |
| Received variance | Population variance of own received output-slot values, within rounding tolerance | Broader nontrivial examples needed |
| Sent variance | Standard population variance matches only two zero-variance references | Two nonzero rows disagree materially; unresolved |
| Fee variance | Matches all four rows | All four allocated-fee sequences have zero variance; denominator remains unidentifiable |

The sent-variance discrepancies are 5.55e12 expected versus 5.2431108875491875e12 extracted, and 5.27e15 expected versus 8.299533293926686e14 extracted. Sample variance also fails to explain these rows. No undocumented correction or missing-value substitution is used to hide the mismatch.

The next step is to obtain the original extractor or raw-record conventions and expand training-only references with nonconstant allocated fees, multiple spends, self-transfers and missing sent extrema. These four development examples cannot certify an adapter. No EFF or BTCPay model score is produced. Do not fill the unresolved variance with zero or a median to manufacture compatibility.

## Reproduction

```bash
python reconcile_training_profiles.py /path/to/Real-CATS new_report.json ../../research/external_cases/pilot_histories_20261013 schema_references_20261014
python -m unittest discover -p 'test*.py'
```

Input checksums and split membership are enforced. Complete-history counts and stable provider counters are rechecked. The new normalized histories preserve original hashes and were checked to reproduce reconciliation. The script is a diagnostic probe, not a certified feature adapter. Existing three benchmark tests and six theft-case tests pass.
