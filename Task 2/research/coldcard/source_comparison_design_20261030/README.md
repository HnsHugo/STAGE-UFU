# Source-address comparison and evaluation design — 30 October 2026

This unit freezes a concrete exploratory target, same-period input-source
selection and evaluation rules before comparison sampling or fitting. It serves
[the address-model objective](../../../ALIGNMENT.md) using the
[500-source feature/evidence view](../source_dataset_20261030/README.md).

The subsequent [selection execution](../source_comparison_selection_20261030/README.md)
has now recovered the four blocks, reconciled all 500 case sources and selected
1,000 comparisons from 5,025 eligible sources. The initial readiness audit below
is preserved as the pre-collection state. Comparison histories and fitting remain
pending.

## Target and its meaning

`known_coldcard_core_membership` is 1 for the fixed 500 corroborated source records.
It is 0 for sampled same-block input sources outside the 505 registry sources and
known collector. Zero means outside that fixed core, **not legitimate, unrobbed,
non-Coldcard or safe**. Actual compromise/device fields stay null unless separately
supported. The one first-person report remains its own evidence tier.

This is an explicit retrospective case-association proxy. It is a practical first
address-model study, not a redefinition of the ultimate theft/hardware objective.
A model can learn holding behaviour or attacker selection rather than device
identity. There is one incident, and the case distributions were already inspected;
there is no untouched test or independent-incident validation claim.

## Frozen comparison selection

Use the four complete anchored Coldcard blocks. The universe consists of unique
decoded positive-valued **input** source addresses, excluding coinbase inputs.
Output-recipient rankings and transaction-only feature tables cannot replace it.
Keep counts of unresolved input addresses; do not guess their identities.

| Reference block | Fixed case sources | Maximum comparison sources |
| --- | ---: | ---: |
| 960188 | 63 | 126 |
| 960189 | 110 | 220 |
| 960190 | 168 | 336 |
| 960191 | 159 | 318 |
| Total | 500 | 1,000 |

For each eligible comparison address, choose its first occurrence by height, then
lexical TXID. An address appearing in several blocks is selected only once.
Hash-order each first-occurrence stratum with the fixed prefix in the protocol;
select up to twice its case count. Do not borrow across short strata or filter by
balance, age, fees, future UTXO depletion, model score or collection success.
Exclude all 505 saved related source addresses plus the known collector.
Reconcile all 500 positive source/payment anchors, input counts and satoshis
against the complete blocks before sampling. Missing anchors stop selection.

A fresh provider snapshot is allowed after matching the fixed height/hash/time,
transaction completeness and case anchors. Record its hash and whether its raw
bytes equal the historical snapshot; different bytes are not historical reproduction.
The existing validator provides structural/provider checks, not cryptographic
inclusion proof.

## Features, failures and evaluation

Keep the same fourteen features and strict `history_height < reference_height`
cutoff for both cohorts. Do not use reference transactions, recipients, block
metadata, role/evidence labels, report dates or collection metadata as predictors.
Plan one bounded history attempt per fixed comparison source: Blockstream,
16 pages, 15-second timeout, two workers and batches of twenty. Preserve failures
and incomplete histories, with no replacement. Audit completion and page-limit
attrition by membership and block before any complete-case model.

Future grouping is conservative overlap prevention: connected components of
repeated addresses, shared prior transaction references, common reference TXIDs
and identical full feature vectors. These components are not ownership claims.
Hash components once into 70% training / 10% validation / 20% test buckets using
the frozen rule. Large components or insufficient class counts cause an explicit
infeasible result; do not reroll seeds or split linked components for better metrics.
Current case-profile inspection makes this exploratory even after grouping.

The first learned baseline is one decision tree: depth 3, at least 20 samples per
leaf, balanced class weights and seed 42; no parameter search. Compare it with a
constant score and two transparent single-feature rankings: prior inactivity and
balance. All fourteen original features and their missingness indicators remain
available; fit imputation on training rows only. The exact model/split gates and
parameter values are in the protocol. No GNN or replacement of the external
19-feature forest is introduced.

Report AP/ROC-AUC and, for the tree at score >= 0.5, precision/recall/F1 **for sampled
core membership only**. The intended 2:1 sampling ratio and completion affect the
observed class prevalence. Scores are not calibrated theft probabilities; none
of these metrics establish theft/device performance or blockchain-wide prevalence.
For the ultimate target, independently supported labels and cross-incident
assessment remain a separate evidence gap. CryptoBilis was already explored;
it is not an untouched external test.

## Artifacts and execution status

- [Protocol](protocol.json): pinned inputs, four block anchors, quotas, target,
  collection bounds, predictor allowlist, evaluation and exact tree parameters.
- [Initial readiness audit](readiness.json): the design reconciles 500 case rows
  and fourteen features; the four complete block cache files were absent at audit.
  This historical audit does not claim a comparison population, sample or model.
- [Selector](../source_comparison_design.py) and [tests](../test_source_comparison.py).

The selector is executable without training or background collection:

```bash
python "Task 2/research/coldcard/source_comparison_design.py" select \
  "Task 2/research/coldcard/source_comparison_design_20261030/protocol.json" \
  "Task 2/research/coldcard/source_cohort_work_comparison_20261030/blocks" \
  /path/to/new-selection.json
```

Use `verify` with the same arguments to reproduce the selected bytes. Public
outputs use address/payment hashes; exact identifiers are re-created locally
from the same block cache. The selector has no network or model-fitting side effect.

## Method references

The scikit-learn documentation supports [training-only preprocessing](https://scikit-learn.org/stable/common_pitfalls.html),
[grouped evaluation](https://scikit-learn.org/stable/modules/cross_validation.html)
and [decision-tree parameter meanings](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html).
The sample sizes, seed, split rule and tree limits are our prespecified design
choices, not settings established as optimal by those documents.
