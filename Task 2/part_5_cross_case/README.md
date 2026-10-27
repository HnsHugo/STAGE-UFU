# Part 5 — Add a second case and evaluate transfer

[Previous: Part 4](../part_4_validation/README.md) · [Main path](../README.md)

## Goal and current status

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

## Proposed next steps, not executed experiments

1. Use the completed [Coldcard source registry](../research/coldcard/source_registry_20261027/README.md)
   and build cutoff-safe source-history features; do not repeat the registry.
2. Recover source-supported CryptoBilis identifiers and record unresolved roles
   and hardware evidence rather than transferring the collectors' labels.
3. Define compatible address features, prediction cutoffs and incident/entity
   groups; assess whether labels support supervised training.
4. Prespecify interpretable baselines and an honest case/temporal transfer
   evaluation; justify graph-model hypotheses from related work.
5. Reproduce and compare Ivan's code when supplied. Its absence does not block
   the registry or source reconstruction.

See the [article map](../docs/ARTICLE_MAP.md) for the Overleaf sections supported by current work. A GNN remains an option to investigate, not an architecture whose success has been demonstrated.
