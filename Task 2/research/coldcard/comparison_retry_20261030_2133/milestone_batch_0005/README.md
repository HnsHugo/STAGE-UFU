# Foreground repair — first 100 sources

This immutable snapshot records five verified batches: 100 attempted, 85 complete,
15 incomplete and zero errors. All 100 raw responses re-extract. The
[combined view](address_dataset.json.gz) and [summary](combined_summary.json)
retain 500 unchanged complete cases and 591 complete comparisons, plus 128
incomplete comparisons, one latest known error and 280 never attempted.
All prior pass outcomes remain explicit. Complete comparisons now cover all four
reference blocks (99, 174, 286 and 32). No model/split or label promotion.

This is a saved progress point; foreground collection may continue afterward.
The configured ChatGPT task had no recorded scheduled execution and two immediate
tests were observed in failed state without detailed results. The foreground
collector is the actual execution evidence; task configuration is not proof of
successful background collection.
