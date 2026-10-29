# Part 2 — Build and understand the dataset

[Previous: Part 1](../part_1_case_study/README.md) · [Main path](../README.md) · [Next: Part 3](../part_3_classifier/README.md)

## Goal

Know what one row represents, where labels come from and which features a classifier receives.

**Address dataset stage:** the [source registry](../research/coldcard/source_registry_20261027/README.md)
is now built: 500 candidate-day source addresses / 1,324 input observations, plus
five later addresses retained separately. All compromise/hardware labels remain
unknown; the transaction corpus below still describes a different observation
unit. The [pre-payment pilot](../research/coldcard/prepayment_pilot_20261027/README.md)
now supplies fourteen cutoff-safe features for eight complete source histories;
the [multi-input extension](../research/coldcard/multiinput_pilot_20261028/README.md)
adds four more complete histories with unchanged definitions. The
[resumable cohort](../research/coldcard/source_cohort_20261028/README.md) now covers
178 complete histories, 14 retained errors, 0 incomplete histories and 308 pending sources. Next: automatic continuation of fixed twenty-source batches. See [Alignment](../ALIGNMENT.md).

## Inputs and coverage

The supplied corpus contains 98 selected blocks and 493,571 unique transactions. It is not the entire blockchain or the entire history of every address. The saved feature CSV is supplied separately and identified by SHA256; [Data access](../DATA_ACCESS.md) lists the required inputs.

| Relation recorded in the feature corpus | Rows | Interpretation |
| --- | ---: | --- |
| Source-attributed consolidation | 5 | Linked to the case by an external investigation |
| Direct-parent candidate | 1,070 | Funding relation to a source-attributed transaction |
| Unattributed | 492,496 | Unknown relation; not certified legitimate |

There are 98 coinbase transactions. The grouped classifier excludes coinbase and the five consolidations, leaving 493,468 rows. The course exercise uses a different, smaller sample and a different payment-to-address target.

## Two feature sets — keep them separate

- **Course exercise, 10 features:** size (bytes), weight (weight units), fee (satoshis), output sum/minimum/maximum/mean/population standard deviation (satoshis), input count and output count. The course slide's `v` is interpreted as output values; this interpretation is documented.
- **Extended Coldcard experiment, 16 features:** counts, address-count/missingness fields, input/output totals, fee, virtual size, fee rate, version, lock time and output statistics. These are transaction features, not the 22-feature Real-CATS address profiles.

## Read and inspect

- [Feature definitions and descriptive checks](../research/coldcard/FEATURE_ANALYSIS.md).
- [Saved corpus manifest](../research/coldcard/inputs_20261008/manifest.json).
- [Label protocol](../research/coldcard/LABEL_PROTOCOL.md).
- [Dataset audit](../research/coldcard/grouped_results_20261008/dataset_audit.json).

## Code

[extract_features.py](../research/coldcard/extract_features.py), [extract_candidate_groups.py](../research/coldcard/extract_candidate_groups.py) and [audit_dataset.py](../research/coldcard/audit_dataset.py) implement extraction, grouping and checks. From the repository root:

```bash
python "Task 2/research/coldcard/audit_dataset.py" \
  /path/to/transactions.csv.gz /path/to/manifest.json /path/to/candidate_groups.json
```

The audit checks the supplied version. A genuinely new dataset requires its own documented provenance and experiment; do not replace a checksum merely to bypass validation.

## What to explain

“The labels describe observed relationships to this case. Transaction IDs, relation labels and block metadata are not used as classifier predictors. The feature units and coverage are explicit.”
