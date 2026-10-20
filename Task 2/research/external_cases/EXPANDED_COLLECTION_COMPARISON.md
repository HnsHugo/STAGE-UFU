# Expanded collection comparison — 20 October 2026 UTC

## Work performed

The previously supplied FSF history was recovered and its **6,947,549 bytes**
match SHA256 `133144439843f6407c4e797b79db4c12205bbcb3c6fd510c2ca778e9aa64eae9`.
The 2,593 confirmed transactions, including two coinbase receipts, pass the
existing provider-counter checks. No public-API recollection or forest scoring
was performed. The raw history remains excluded from Git; it is supplied
separately as documented in [data access](../../DATA_ACCESS.md).

The same 24-hour observation protocol now covers **two incident groups and two
documented donation-purpose comparison entities**: five addresses, nine windows.
Repeated windows are not additional independent entities. The six observations
from the [first comparison](TEMPORAL_COLLECTION_COMPARISON.md) reproduce unchanged.
New registry schema 2 records cohort counts instead of carrying the earlier
single-comparison description into a larger cohort.

## Additional measured observations

| FSF window, UTC | Receipt transactions | Gross BTC received | Exactly-one-output funding share | Largest-block receipt share | Spending transactions |
| --- | ---: | ---: | ---: | ---: | ---: |
| 30 July 2026 | 0 | 0.00000000 | n/a | n/a | 0 |
| 9 October 2026 | 1 | 4.00000000 | 0% | 100% | 0 |
| 6 May 2011, retrospective stress day | 25 | 237.20737514 | 24% | 8% | 1 |

Stress selection follows the existing policy: maximize receipt count among UTC
calendar days strictly before 10 October 2026, breaking ties by earliest date.
It uses no model score or tuned detection threshold. Both incident-day windows
are retained, including the inactive window. Receipts are gross address receipts,
which can include change/self-transfers; these are not counts of donors or
externally verified donations. Input-address counts do not identify people.

The expanded [result JSON](collection_expanded_20261020/comparison.json) contains
all exact values, group identifiers, hashes, provider audits and 36 pairwise
window-overlap checks. No shared transaction or input address was observed
between different groups within these selected windows. This is narrower than
an entity/case independence proof, and differs from historical overlaps with
the separate Real-CATS training corpus.

## What this does and does not establish

FSF provides a more active stress observation than EFF's maximum of two receipts.
Its 25 receipts are distributed across blocks over 81,291 seconds, whereas the
three case collectors have 500, 76 and 46 first-day receipts spanning 918, 1,285
and zero confirmation-timestamp seconds respectively. These are descriptive
differences in this small cohort, not validated rules or performance estimates.

The FSF stress day is in **2011**. Fee conditions, address age and calendar dates
are not matched to the 2026 incidents. Its zero median incoming fee rate must
not become a hardware fingerprint. Both comparison organizations are donation
recipients; busy exchanges, merchants and other collection contexts remain
unrepresented. Two purpose-documented entities cannot establish specificity or
precision. No absence of reported crime is converted into a legitimate label.

No model is trained, no threshold is selected and the frozen 19-feature model
and its 0.15 threshold remain unchanged. CryptoBilis stays one incident group;
the professor-supplied participant story does not create another independent case.

## Reproduction and tests

Place the separately supplied, checksum-matching FSF file at
`Task 2/research/external_cases/fsf_history_20261014.json.gz`. From that directory,
choose a new output path:

```bash
python compare_collection_patterns.py collection_expanded_20261020/registry.json \
  /tmp/new_expanded_collection_comparison.json
python -m unittest discover -p 'test_*.py' -v
```

The expanded real-data reproduction test explicitly skips when the separate FSF
file is absent; the code, saved results and all other tests remain accessible.
With the supplied file present, this session executed it successfully. A new
boundary test rejects a split group used as both incident and comparison entity.
The repository-wide verification report records the complete test run.

All **161 tests passed**, including the expanded real-data reproduction test.
The [execution log](../../verification/expanded_collection_20261020.json) records
all six suites; 185 protected historical artifacts retain their hashes.

## Next priority

Seek documented, contemporary collection recipients with higher daily throughput
and additional entities. Fix their selection/observation policy before scoring.
Retain the two incident groups as groups, and do not fit a supervised detector
on this small purpose-based comparison cohort merely to produce a favorable F1.
