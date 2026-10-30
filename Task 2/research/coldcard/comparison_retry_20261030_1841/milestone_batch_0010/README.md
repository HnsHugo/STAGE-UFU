# Ten retry batches — immutable 200-source milestone

This snapshot is reconstructed from the first ten immutable deltas of
[the active retry](../README.md), without API requests. It retains 200 attempts:
174 complete, 26 incomplete, zero errors and 453 pending in this pass. All 200
raw responses were re-extracted locally. The earlier
[first-four-batch milestone](../milestone_batch_0004/README.md) remains intact.

The [combined summary](combined_summary.json) and
[address view](address_dataset.json.gz) retain all 1,500 selected addresses and
every preceding pass outcome. There are 947 complete feature vectors: 500
unchanged cases and 447 complete comparisons. Comparisons also have 100
incomplete histories, 173 latest known errors and 280 never attempted. No
unknown label is promoted, and no model or split is created. Collection continued
after this historical milestone; later root exports supersede its coverage.

Use the same protocol with this directory as the output to verify or restore
the normalized checkpoint offline. Raw addresses and full histories remain
excluded from publication.
