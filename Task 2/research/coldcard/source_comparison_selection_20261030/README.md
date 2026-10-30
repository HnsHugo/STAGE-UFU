# Same-block source comparisons selected — 30 October 2026

The [frozen design](../source_comparison_design_20261030/README.md) is now executed
through actual comparison selection. Four complete anchored blocks were retrieved
from the documented Blockchain.info path. All 500 case source/payment records
reconcile by block, input address, input count and integer input value. No model
or comparison-address history was collected in this unit.

| First-reference block | Case sources | Eligible comparisons | Selected |
| --- | ---: | ---: | ---: |
| 960188 | 63 | 427 | 126 |
| 960189 | 110 | 678 | 220 |
| 960190 | 168 | 2,048 | 336 |
| 960191 | 159 | 1,872 | 318 |
| Total | 500 | 5,025 | 1,000 |

The four blocks contain 22,994 transactions, including four coinbases, and 31,915
decoded positive-valued input observations. There are 5,526 distinct input source
addresses before exclusions and no unresolved input-address observations in these
responses. Of the 506 addresses on the exclusion list (505 registry sources plus
collector), 501 occur in the census. The eligible pool is therefore 5,025 unique
sources, with no quota shortfall and no repeated selected address.

Comparison rows have `known_coldcard_core_membership=0`, **not a legitimate or
non-hardware label**. Actual compromise/hardware fields remain null. All 1,000
feature vectors are pending: this extends the fixed selection to 500 case sources
plus 1,000 comparisons, not to 1,500 feature-complete records.

## Saved evidence and reproduction

- [Selection](selection.json): 1,000 hashed source/payment records, cutoffs,
  unknown compromise/device fields, pool sizes and block snapshot hashes.
- [Redacted census](census.json.gz): all 5,526 first-source observations, hashed
  identifiers, salted selection keys and exclusion flags. It reproduces selection
  without private raw block files; it is a normalized provider-derived snapshot,
  not a cryptographic inclusion proof or independent re-verification of the blocks.
- [Block retrieval record](block_collection.json): URLs, checks, sizes and hashes.
- [Execution verification](../../../verification/source_comparison_20261030.json).

The new block responses differ byte-for-byte from the 20 October responses.
Their original historical hashes/results are preserved; this is a fresh snapshot,
with matching fixed height/hash/time anchors, transaction counts and exact case
input/value agreement. Raw block JSON remains in the ignored local cache. The
public redacted census preserves the sampling evidence even if provider metadata
changes or that raw cache is unavailable later.

From the repository root, reproduce the selected bytes from public inputs:

```bash
python "Task 2/research/coldcard/source_comparison_design.py" replay \
  "Task 2/research/coldcard/source_comparison_design_20261030/protocol.json" \
  "Task 2/research/coldcard/source_comparison_selection_20261030/census.json.gz" \
  "Task 2/research/coldcard/source_comparison_selection_20261030/selection.json"
python -m unittest discover -s "Task 2/research/coldcard" -p "test_source_*.py"
```

With the exact block cache, `verify` instead of `replay` independently regenerates
the census and selection from raw block contents. A separate aggregation/minimum
reference/hash-order check also confirms all 1,000 selected records and exclusions.
Sixty source-path tests pass. The pipeline does not use model scores or history
completion to choose these addresses.

## Next unit

Implement bounded, resumable history collection for this fixed 1,000-source plan,
reusing the existing collector/extractor where compatible. Retain one selected
row per source even when requests fail or the history is incomplete. Use the
same fourteen strictly prior-block features and document attrition before any
fitting. No replacement, refitting of the existing external forest or random
within-incident validation claim is authorized by the selection result.
