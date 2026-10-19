# Preparing a hot / cold comparison

Audit dated 5 October 2026. Data examined: [address_summary.csv](results/history_20261005/address_summary.csv), version [d8cff427](https://github.com/HnsHugo/STAGE-UFU/commit/d8cff427001d21c0fbe07efd97bf944c8cebe4c7).

## Finding

The collection can describe observed transactions. It does not yet support a validated comparison of hot / cold behaviour over a shared period: histories are truncated differently and no shared interval of label validity has been established.

The 25 Bitfinex hot transactions span 9.73 hours. The 25 transactions for its two cold addresses span 55.01 and 251.01 days respectively. These durations measure the distance between the sample's earliest and latest dates, not a complete observation window. Dividing 25 by these durations does not give a comparable frequency: windows were selected by event count.

## Coverage by address

Dates and durations are in UTC. Duration = (newest_observed_utc - oldest_observed_utc) / 86400, rounded to two decimal places in days. Displayed dates omit the time; durations use the CSV's complete timestamps.

| Entity | Address | Published label | Observed transactions | Earliest / latest dates | Span (days) | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| BTC-e.com | `16SbwNa22nBwhLtg6HzWVYFQiUxtNzAUpt` | unknown | 25 | 2016-04-03 → 2016-04-25 | 21.93 | partial |
| Bitfinex | `1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g` | hot | 25 | 2026-10-04 → 2026-10-05 | 0.41 | partial |
| Bitfinex | `3JZq4atUahhuA9rLhXLMhhTo133J9rF97j` | cold | 25 | 2026-08-07 → 2026-10-01 | 55.01 | partial |
| Bitfinex | `bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97` | cold | 25 | 2025-12-20 → 2026-08-28 | 251.01 | partial |
| Binance | `34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo` | unknown | 25 | 2026-07-03 → 2026-09-19 | 78.22 | partial |
| Binance | `3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb` | unknown | 25 | 2026-02-01 → 2026-08-28 | 208.68 | partial |
| Binance | `3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6` | unknown | 25 | 2026-08-06 → 2026-09-22 | 47.81 | partial |
| Binance | `bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h` | unknown | 25 | 2026-10-05 → 2026-10-05 | 0.02 | partial |
| Change | `bc1q43krjn8qvfydqs9lq8crg26er4c26hkpd2mpw7` | cold | 2 | 2025-01-16 → 2025-09-10 | 236.59 | count_matches_stable_stats |
| Change | `bc1qhsuvec03zslh9qvauksh2wc9hy9za7csxem5ea` | cold | 2 | 2025-03-04 → 2025-04-30 | 57.18 | count_matches_stable_stats |
| Change | `bc1q9rqfux88j6az0wl957u2jdykgw5m5r72hcaclu` | cold | 2 | 2025-03-10 → 2025-05-15 | 65.55 | count_matches_stable_stats |

The eight partial histories are insufficient to establish that a transaction absent from the sample does not exist. The three Change histories have counts consistent with stable provider statistics; this remains a consistency check, not a guaranteed atomic snapshot.

## Evidence dates

| Group | Available evidence | Use in the comparison |
| --- | --- | --- |
| Bitfinex: 1 hot, 2 cold | Versioned official list; operational interval unspecified | Retain published labels, but their applicability to 2026 transactions remains unverified |
| Change: 3 cold | Snapshot at 31 March 2025, 23:59 UTC | The label is supported at that instant; continuity before or after is not established |
| Binance: 4 unknown | Reserves at 10 November 2022; no per-address label | Exclude from hot/cold groups; do not infer storage from activity |
| BTC-e: API test | WalletExplorer attribution, unknown storage | Exclude from the research sample |

Sources and limitations: [Bitfinex and Binance](data/research_sources_20261005.md), [Change](data/change_sources_20261005.md), [collection method](HISTORY.md). reviewed_at_utc is the date the source was read, not the beginning of label validity. Therefore, this audit selects no calendar period as “validated hot/cold.”

## Protocol for the next collection

1. Establish evidence-validity dates for hot and cold addresses. Record the snapshot date, supported interval if available, and assumptions separately. A snapshot alone does not justify a 30-day interval.
2. Fix a shared window [inclusive UTC start, exclusive UTC end] before inspecting results. A 30-day duration is an exploratory proposal to adapt to the evidence; it is not a validated period at this stage.
3. Collect until the window's start is covered or the history is exhausted, with an explicit request cap. If the cap is reached before coverage, mark the window incomplete and leave complete metrics unavailable. The current collector is page-limited and does not yet implement this window-based collection.
4. Check boundaries using block heights and deduplicate TXIDs. Block timestamps can be non-monotonic: a single old timestamp encountered during pagination does not by itself prove coverage. Document chain changes between requests.
5. Compute the metrics below only for covered windows. Explicitly identify exploratory results that use historical labels.

| Planned measure | Definition |
| --- | --- |
| Transaction count | Distinct TXIDs involving the address within the window |
| Daily frequency | Count / fixed window duration in days, including days without transactions |
| Inflows / outflows | Sum of values attributed to this address, in satoshis; returns included |
| Active days | Number of UTC dates with at least one confirmed transaction |
| Median fee rate | Median sat/vB of transactions spending funds from the address; whole-transaction fees, not fees allocated to the address |
| Receive-only transactions | Separate count; their fees are selected by the sender and do not describe the recipient's policy |

Zero requires a covered window: no observation in a truncated history means “unavailable,” not zero. An address may represent only part of a wallet. Small unsolicited receipts may inflate activity without reflecting a decision by its owner.

## Scope of conclusions

The sample contains ten research addresses: five cold, one hot and four unknown. The three entities are not a representative population. The only hot address belongs to Bitfinex, so entity and storage type may be confounded. Multiple addresses from one entity are not independent observations. Present results by address and entity first; expand both groups before generalizing.

All hardware and illicit labels remain unknown. This audit computes neither an illicitness score, CPFP nor UTXO holding duration. The latter two analyses require additional input/output data.
