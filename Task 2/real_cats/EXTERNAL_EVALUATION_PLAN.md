# Independent evaluation readiness

The registry membership audit is reproducible with audit_external_candidates.py. It verifies raw source checksums and compares addresses against the original split. It does not construct test features, predict test labels, or inspect test outcomes.

| Candidate source | Addresses | Existing split overlap | Readiness |
|---|---:|---|---|
| Real-CATS registry | 1,361 | 818 train, 269 validation, 274 reserved test | Already in the benchmark; not a new independent dataset |
| Coldcard research | 597 | None in either full Real-CATS source file | Pending role review; one conservative incident group |
| BTCPay research | 2 | None in either full Real-CATS source file | Pending role review; one incident group |

Zero address overlap does not establish different ownership or incident independence. The two external repositories do not provide an independently verified benign comparison cohort. Hundreds of addresses from one incident must not be reported as hundreds of independent cases. The earlier six-address collection pilot includes four Real-CATS examples, so it is not an independent six-address evaluation.

## Frozen candidate

Preserve the exploratory validation winner: 100-tree random forest, depth 20, minimum leaf size 20, sqrt feature sampling, positive class weight 1, seed 42, training-only median imputation with missingness indicators, and strict score > 0.15. Do not adjust these settings using external evaluation outcomes. The baseline remains the weight-3 forest without indicators, strict score > 0.30. Neither model has an independently confirmed improvement yet.

## Data preparation sequence

1. Review external source evidence at address level. Store source URL, incident ID, role, confidence, and the date the attribution became available. Keep victims separate from reported receiving/collector addresses; unresolved addresses remain unknown.
2. Define the target explicitly: a Real-CATS source-category benchmark and verified stolen-fund recipient detection have different labels. External case results can be a stress test, not automatically an equivalent benchmark.
3. Build an independently sourced comparison cohort with documented selection and evidence. No abuse report is not proof of legitimacy. Match relevant calendar periods and observation maturity; disclose uncertainty and selection bias.
4. Collect histories under a fixed observation policy. The current model uses full-history profiles; the existing 24-hour snapshots are not interchangeable with its 22 features. Reproduce the source definitions and monetary units before scoring. A decision-time model requires a separate training/evaluation experiment using cutoff-safe features throughout.
5. Check address, entity, shared-transaction and incident overlap. Reserve entire cases and comparison groups. Keep their labels out of model selection.
6. Evaluate frozen configurations once, reporting TP/FP/FN/TN, precision, recall, F1, ranking metrics and per-case detection. Report case count, label confidence, observation coverage and comparison prevalence. A positive-only sample supports descriptive detection coverage but cannot estimate precision or false-positive rate.

No independent score is reported in this step. The next concrete collection priority is evidence review of the two BTCPay collectors and selection of independently documented comparison groups; the 597 Coldcard addresses remain one conservative case group.

## Reproduction

```bash
python audit_external_candidates.py /path/to/Real-CATS ../theft_cases/research_candidates_20261013.json external_candidate_audit.json
```
