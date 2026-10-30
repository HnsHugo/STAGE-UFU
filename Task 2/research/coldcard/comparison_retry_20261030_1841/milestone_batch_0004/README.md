# First four retry batches — immutable milestone

This snapshot is reconstructed exclusively from the first four immutable batch
deltas of [the active retry](../README.md), without API requests. It preserves
80 attempts: 70 complete, 10 incomplete and zero errors, with 573 still pending
in this 653-source pass. All 80 raw responses were re-extracted locally.

The [combined summary](combined_summary.json) and
[address view](address_dataset.json.gz) retain all 1,500 selected addresses, all
earlier pass outcomes and 843 complete feature vectors: 500 cases and 343
comparisons. The original 500 case vectors, 273 earlier complete comparisons
and 74 earlier incomplete histories remain unchanged. Unknown labels stay
unknown; no model or split is created. This milestone is historical; later root
checkpoints supersede its coverage while these bytes remain intact.

Use the same protocol with this directory as the output to verify or restore
its normalized checkpoint offline. Raw addresses/histories are excluded from
publication. Collection was still running when this milestone was taken.
