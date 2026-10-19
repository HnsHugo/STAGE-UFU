# Part 5 — Add a second case and evaluate transfer

[Previous: Part 4](../part_4_validation/README.md) · [Main path](../README.md)

## Goal and current status

Extend the case study with sourced examples and evaluate on a case kept outside training. Hugo's meeting notes mention Ledger, address tracking and combining another case with Coldcard. **The exact incident reference and Ivan's code are still pending.** No Ledger dataset or hardware-wallet classifier is claimed to be completed.

## Before adding addresses

Record the source, publication date, event period, exact address/TXID and role: victim, collection address, consolidation or later destination. Keep role confidence separate from hardware-device evidence and storage type. A case involving a hardware-wallet user does not mean every recipient uses that device.

Preserve case and entity identifiers. A proposed extension should keep complete cases/groups apart during evaluation. Shuffling all transactions from both cases into both training and test would not establish cross-case generalization. Features and labels must be available by the prediction date for a prospective claim.

## Existing work that can help

- [Label protocol](../research/coldcard/LABEL_PROTOCOL.md).
- [External evidence and collection tools](../research/external_cases/README.md).
- [External evidence review](../research/external_cases/EXTERNAL_EVIDENCE_REVIEW.md).
- [Historical independence/overlap audit](../supplementary/real_cats/EXTERNAL_INDEPENDENCE_AUDIT.md).

FBI, Binance, donation addresses and the other saved pilots are different evidence contexts. They are not automatically hardware-wallet training examples. Their source-category scores should not be merged with the Coldcard transaction target.

## Proposed next steps, not executed experiments

1. Read the actual case references and annotations in Overleaf; the main LaTeX file alone does not include their contents.
2. Reproduce Ivan's code with its original dataset, target and split when provided.
3. Compare those definitions with Parts 2–4 before changing the model.
4. Construct a separately versioned case registry and dataset.
5. Prespecify a case-held-out evaluation and any graph-based hypotheses.

See the [article map](../docs/ARTICLE_MAP.md) for the Overleaf sections supported by current work. A GNN remains an option to investigate, not an architecture whose success has been demonstrated.
