# Part 5 — Add a second case and evaluate transfer

The [completed frozen CryptoBilis transfer](../research/external_cases/cryptobilis_frozen_transfer_20261104_215520/README.md) gives membership F1 **0.629834** (57 TP / 151 TN / 2 FP / 65 FN) on the exact 275 eligible sources. Precision is 0.966102 and recall 0.467213; inactivity ranking has higher AP than the frozen tree (0.854026 vs 0.688142). The model, preprocessing and >=0.5 threshold are unchanged. All 54 quarantined complete vectors and 37 bounded prefixes remain unscored. This is one inspected structural-proxy incident with unknown theft/device labels; the next unit is the scientific write-up.

The [4 November source overlap/eligibility audit](../research/external_cases/cryptobilis_overlap_20261104_205032/README.md) reproduces both cohorts and the frozen Coldcard partitions. Four measured cross-development components quarantine 54 complete comparison vectors; 37 prefixes remain null. The 275 eligible external vectors pass the prespecified overall support gate. The subsequent frozen-model source inference is completed above; the overlap result itself performed no scoring.

[Previous: Part 4](../part_4_validation/README.md) · [Main path](../README.md)

## Goal and current status

**Bounded acquisition closed — 4 November 2026:** The [final CryptoBilis source audit](../research/external_cases/cryptobilis_reference_prefix_20261104_201345/README.md) covers all 366 fixed sources: 329 complete prior-prefix vectors (122 case / 207 comparison), 37 bounded-incomplete comparisons without vectors, no network or unattempted sources. Every raw tail/vector is independently checked, all prior results are preserved and automations remain disabled. The subsequent overlap audit above excludes 54 complete comparisons and leaves 275 eligible vectors. Full-current-history reconciliation, verified victim/device labels and entity independence remain separate limitations. The later fixed-proxy metrics are reported above; no new fit occurred.

**Historical readiness snapshot — 2 November 2026:** The
[CryptoBilis source registry and transfer protocol](../research/external_cases/cryptobilis_source_readiness_20261102/README.md)
recover 122 source candidates from 122 event payments / 140 input outpoints.
Labels remain graph candidates with unknown independently verified compromise
and device status. The protocol fixes 244 planned same-block comparisons, the
original fourteen definitions and the unchanged Coldcard model/preparation.
Both collectors stay in one external incident outside fitting. At that checkpoint, outputs
contained zero comparison selections, source-feature vectors or scores; no new F1.
Ten tests and independent offline recount pass. Exact address/reference and
observed funding overlaps are zero, while complete prefix/entity overlap remains
pending at that historical checkpoint. Census, bounded acquisition and the
available-prefix overlap/quarantine audit have since completed as described above;
entity independence remains unestablished.

The [Coldcard source-address write-up](../source_address_study/README.md) now
documents the completed single-incident membership baseline. It supplies a
reproducible starting point, not cross-case validation. A future source-address
extension must define compatible evidence, roles, cutoffs and incident-level
evaluation before new model fitting; the existing test outcomes stay fixed.

Extend the **source-address** dataset with sourced examples and evaluate transfer
across cases. **CryptoBilis is the intended second incident.** The Teams objective
is now explicit: after the transaction exercise, build the dataset and model of
robbed source addresses, with hardware evidence kept separate. Read
[Alignment](../ALIGNMENT.md). Ivan's code and exact source/device mappings remain
pending; no validated hardware-wallet classifier is claimed. CryptoBilis has
already been explored and is not an untouched final test case.

## Before adding addresses

Record the source, publication date, event period, exact address/TXID and role: victim, collection address, consolidation or later destination. Keep role confidence separate from hardware-device evidence and storage type. A case involving a hardware-wallet user does not mean every recipient uses that device.

Preserve case and entity identifiers. A proposed extension should keep complete cases/groups apart during evaluation. Shuffling all transactions from both cases into both training and test would not establish cross-case generalization. Features and labels must be available by the prediction date for a prospective claim.

## Existing work that can help

- **Start here:** [Source-first alignment and next unit](../ALIGNMENT.md).
- [Historical complete-block recipient ranking](../CENTRAL_EXPERIMENT.md): supporting destination results, not a source-address classifier.
- [Expanded comparison](../research/external_cases/EXPANDED_COLLECTION_COMPARISON.md): EFF plus FSF, with two purpose-documented entities and an explicit 2011/2026 temporal mismatch; the original observations remain unchanged.
- [Equal-duration temporal comparison](../research/external_cases/TEMPORAL_COLLECTION_COMPARISON.md): the same feature extractor on Coldcard, the provisional case and a documented donation recipient, including counterexamples and observation limits.
- [New collection-pattern pilot](../research/external_cases/COLLECTION_PATTERNS.md): two source-attributed recipients, cutoff-safe measurements and reproducible public observations. The case selection is now resolved; address-specific hardware labels and classifier validation remain unresolved.
- [Label protocol](../research/coldcard/LABEL_PROTOCOL.md).
- [External evidence and collection tools](../research/external_cases/README.md).
- [External evidence review](../research/external_cases/EXTERNAL_EVIDENCE_REVIEW.md).
- [Historical independence/overlap audit](../supplementary/real_cats/EXTERNAL_INDEPENDENCE_AUDIT.md).

FBI, Binance, donation addresses and the other saved pilots are different evidence contexts. They are not automatically hardware-wallet training examples. Their source-category scores should not be merged with the Coldcard transaction target.

## Completed stages and next unit

1. Reuse the completed [Coldcard source study](../source_address_study/README.md),
   its fourteen prior-block features and saved membership baseline; do not repeat
   the registry, collection or frozen fit.
2. Reuse the completed fixed CryptoBilis census and bounded acquisition. Preserve
   all 366 outcomes, 37 null bounded prefixes and the graph-candidate label tier;
   do not restart the exhausted collection or replace unavailable comparisons.
3. Reuse the completed overlap/quarantine manifest: exactly 122 cases and 153
   comparisons are eligible. Preserve all 54 quarantined complete vectors and
   37 unavailable prefixes; report complete-case and quarantine attrition.
4. The prespecified frozen-model inference and comparator evaluation are complete.
   Preserve the F1 0.629834 result, all 67 errors and the stronger inactivity ranking;
   integrate them into the scientific write-up. Do not tune on this inspected case
   or claim verified theft/device or untouched independent validation.
5. Reproduce and compare Ivan's code when supplied. Its absence does not block
   the registry or source reconstruction.

See the [article map](../docs/ARTICLE_MAP.md) for the Overleaf sections supported by current work. A GNN remains an option to investigate, not an architecture whose success has been demonstrated.
