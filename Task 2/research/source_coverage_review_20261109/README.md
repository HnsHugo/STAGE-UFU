# Offline coverage inventory after the supervision update

Recorded 9 November 2026. The new [research direction](../../docs/MEETING_FEEDBACK_20261109.md)
prioritizes covering the missing selected observations, bounded tabular transfer
experiments, graph/deep-learning versions of the same cohorts, and a separate
test of a possible pre/post-Coldcard exchange-directed activity change.

This unit pins the existing published exports at commit
`04aae8dd928241fc422fb9bf47e5fae3f1c20bd9` and recounts their contents offline.

| Dataset | Selected | Available vectors | Bounded-incomplete |
| --- | ---: | ---: | ---: |
| Coldcard | 1,500 | 1,378 | 122 |
| CryptoBilis | 366 | 329 | 37 |
| Total | 1,866 | 1,707 | 159 |

All missing vectors belong to comparison sources. Their exact existing IDs
are retained in [coverage_inventory.json](coverage_inventory.json), and match
the published stopped checkpoints exactly. Both old network ID lists are empty;
new coverage work must have a separate scope and protocol. The 54 complete
CryptoBilis vectors quarantined for observed links are a separate exclusion.

The auditor verifies compressed export fingerprints, schema-v2 identities,
distinct sources, identical 14-column allowlists, complete versus null-vector
statuses, class counts, unchanged unknown verified labels, checkpoint gap lists
and the saved overlap/policy metadata. It also verifies that the input policy
has an idle lease and disabled historical automation. This is a structural and
coverage check of public exports, not a new audit of private raw histories or
an independent recalculation of all numerical feature values.

Current GitHub-pinned exports were used in a separate review workspace while
preserving the existing recovery checkout and its prior modifications. A later
collection unit must locate and verify the documented original private
evidence and successful cached pages before deciding which requests are needed.

No provider request, new fit, score, graph or migration result was produced.
No historical collector was restarted and no automation was enabled. The input
fingerprints and all historical artifacts are preserved.

From the repository root, reproduce without provider access or model imports:

```sh
python "Task 2/research/source_coverage_review_20261109/audit.py" --check "Task 2/research/source_coverage_review_20261109/coverage_inventory.json"
```

The immediate next unit is a capacity/coverage-extension specification for
these 159 sources and a prespecified CryptoBilis-to-Coldcard experiment using
the current snapshot, with fresh direction-specific overlap and validation
rules. The wider graph/deep-learning study is the main subsequent modeling
priority. The third test incident remains to be selected and frozen.
