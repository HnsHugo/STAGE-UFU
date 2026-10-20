# Part 5 — Add a second case and evaluate transfer

[Previous: Part 4](../part_4_validation/README.md) · [Main path](../README.md)

## Goal and current status

Extend the case study with sourced examples and evaluate on a case kept outside training. **The supplied professor references now identify CryptoBilis as the intended second incident.** Read the [reference review](../research/external_cases/PROFESSOR_REFERENCES.md). Ivan's code, exact participant/device mappings and the final prediction target remain pending; no validated hardware-wallet classifier is claimed.

## Before adding addresses

Record the source, publication date, event period, exact address/TXID and role: victim, collection address, consolidation or later destination. Keep role confidence separate from hardware-device evidence and storage type. A case involving a hardware-wallet user does not mean every recipient uses that device.

Preserve case and entity identifiers. A proposed extension should keep complete cases/groups apart during evaluation. Shuffling all transactions from both cases into both training and test would not establish cross-case generalization. Features and labels must be available by the prediction date for a prospective claim.

## Existing work that can help

- [Expanded comparison](../research/external_cases/EXPANDED_COLLECTION_COMPARISON.md): EFF plus FSF, with two purpose-documented entities and an explicit 2011/2026 temporal mismatch; the original observations remain unchanged.
- [Equal-duration temporal comparison](../research/external_cases/TEMPORAL_COLLECTION_COMPARISON.md): the same feature extractor on Coldcard, the provisional case and a documented donation recipient, including counterexamples and observation limits.
- [New collection-pattern pilot](../research/external_cases/COLLECTION_PATTERNS.md): two source-attributed recipients, cutoff-safe measurements and reproducible public observations. The case selection is now resolved; address-specific hardware labels and classifier validation remain unresolved.
- [Label protocol](../research/coldcard/LABEL_PROTOCOL.md).
- [External evidence and collection tools](../research/external_cases/README.md).
- [External evidence review](../research/external_cases/EXTERNAL_EVIDENCE_REVIEW.md).
- [Historical independence/overlap audit](../supplementary/real_cats/EXTERNAL_INDEPENDENCE_AUDIT.md).

FBI, Binance, donation addresses and the other saved pilots are different evidence contexts. They are not automatically hardware-wallet training examples. Their source-category scores should not be merged with the Coldcard transaction target.

## Proposed next steps, not executed experiments

1. Use the supplied incident references and retain unresolved address roles; other Overleaf sections have not all been supplied.
2. Reproduce Ivan's code with its original dataset, target and split when provided.
3. Compare those definitions with Parts 2–4 before changing the model.
4. Construct a separately versioned case registry and dataset.
5. Prespecify a case-held-out evaluation and any graph-based hypotheses.

See the [article map](../docs/ARTICLE_MAP.md) for the Overleaf sections supported by current work. A GNN remains an option to investigate, not an architecture whose success has been demonstrated.
