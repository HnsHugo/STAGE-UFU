# Parent audit — 8 October 2026

Results provided by Hugo from Codespaces: all five transactions attributed by Bitquery were found. Of 2,349 parent transaction indices searched for, 1,070 were found and 1,279 are missing from the supplied blocks. All recovered parents have one output; 934 have one input, or 87.29%.

The relationships establish neither theft nor hardware-wallet control. Parents remain candidates with unknown labels. Other transactions are not certified legitimate negatives. The supplied data cover 98 selected blocks, not a complete history.

## Extraction in Codespaces

From `Task 2/research/coldcard`, after `git pull`:

```bash
python extract_features.py blocks parents.json features_output
```

The output directory must be new. Check `manifest.json`: status `complete`, 493571 transactions, 5 `source_attributed`, 1070 `direct_parent_candidate`, 492496 `unattributed`. Share `transactions.csv.gz` and `manifest.json` to continue the analysis.

Identifiers, block height and relation must not be used as model features. Relation records provenance, not theft ground truth. The script extracts confirmed transaction properties without future spending status. Virtual size is rounded up from weight. Coinbase transactions are explicitly distinguished.

Training requires a documented labeling strategy and separation of related groups between training and test. No detection performance has yet been demonstrated at this stage.
