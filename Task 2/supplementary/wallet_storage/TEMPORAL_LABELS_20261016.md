# Temporal evidence and snapshot profiles — 16 October 2026

## Bitfinex: direct verification result

The official repository's GitHub API returned two revisions of `wallets.txt` in the accessible history up to the pinned commit:

| Commit | Recorded commit time, UTC | Change |
| --- | --- | --- |
| `e72eec303c93396bdbc7c4fce6cd99f8e1307551` | 2022-11-11 18:59:13 | File created |
| `83d06bdb5f5a2ce05d5ba2db5a426dd44c9f5128` | 2022-12-12 22:24:41 | BSV cold wallet changed |

The three BTC entries were fetched directly from **both versions**: one hot and two cold, matching the pilot addresses. The December edit concerns BSV, not BTC. URLs, dates and factual extracts are retained in `data/storage_temporal_evidence_20261016.json`.

This establishes label assertions in two versions, not a continuously valid operational interval. Git dates are not independent proof of first public availability; even GitHub signature verification does not prove address ownership or key storage. No operational start/end interval or independently timestamped publication was obtained. **No label is extended to September 2026.**

Reproduction query:

`https://api.github.com/repos/bitfinexcom/pub/commits?path=wallets.txt&sha=83d06bdb5f5a2ce05d5ba2db5a426dd44c9f5128&per_page=100`

Files are available at `https://raw.githubusercontent.com/bitfinexcom/pub/<COMMIT>/wallets.txt`. The query bounds the history at the studied commit; later versions were not reviewed in this unit.

## Bounded independent-source search

An official BitMEX lead was examined: the address-reissuance announcement and reserve snapshot. Both primary-page opens returned 404 through the lookup tool. Search snippets were not accepted as label/date evidence. Zero addresses were added. Access failure does not prove that usable sources do not exist; the search stopped to preserve the session budget.

## Executed local work: Change at 31 March 2025

Three saved histories, complete according to provider counters, support point-in-time reconstruction at `2025-03-31T23:59:00Z`, the cold snapshot documented in `data/change_sources_20261005.md`. Only transactions with confirmation timestamps at or before the snapshot contribute features.

| Address suffix | Included transactions | Received (sat) | Spent (sat) | Reconstructed balance (sat) |
| --- | ---: | ---: | ---: | ---: |
| `...hkpd2mpw7` | 1 | 457067 | 0 | 457067 |
| `...csxem5ea` | 1 | 89999708 | 0 | 89999708 |
| `...r72hcaclu` | 1 | 2999999395 | 0 | 2999999395 |

`results/change_snapshot_profiles_20261016.json` retains full addresses and the three input hashes. Current balances and later spending are not used to calculate the features. Time since the last observed transaction is not UTXO holding time.

The label publication is documented as **21 April 2025**, after the snapshot. Its exact time is unknown and remains null. This unit reused the earlier Change source review without new authentication. These are **retrospective** profiles, not prospective training data: completeness uses subsequently collected counters, and the labels were unavailable at the reconstructed date. The three addresses belong to one attributed entity. No classifier or predictive metric is produced.

## Reproduce and test

From the repository root:

```bash
python "Task 2/supplementary/wallet_storage/snapshot_storage_profiles.py" \
  "Task 2/supplementary/wallet_storage/results/window_september2026/bc1q43krjn8qvfydqs9lq8crg26er4c26hkpd2mpw7.json" \
  "Task 2/supplementary/wallet_storage/results/window_september2026/bc1qhsuvec03zslh9qvauksh2wc9hy9za7csxem5ea.json" \
  "Task 2/supplementary/wallet_storage/results/window_september2026/bc1q9rqfux88j6az0wl957u2jdykgw5m5r72hcaclu.json" \
  --snapshot 2025-03-31T23:59:00Z --label-publication-date 2025-04-21 \
  --output /path/to/new_snapshot_report.json
python -m unittest discover -s "Task 2/supplementary/wallet_storage" -p 'test*.py'
```

At that stage, 32 tests passed, including four new checks for future-transaction exclusion, the inclusive boundary, duplicate/incomplete histories and timezone handling.

## Current status

The pinned Bitfinex publication has been checked; do not repeat that work. A snapshot does not establish continuous monthly labels. September training remains blocked, and further source searching is currently paused in favor of the [main case-study path](../../README.md).
