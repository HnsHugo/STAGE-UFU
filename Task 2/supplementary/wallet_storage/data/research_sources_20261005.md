# First sourced research sample — 2026-10-05

## Selection

Seven research addresses were added to the seed table, alongside the existing API
smoke-test row. This is a convenience sample of published exchange wallets, not a
representative sample of Bitcoin users. Two entities are covered; no statistical
cold-versus-illicit inference is possible from these records.

| Entity | Research addresses | Storage labels | Applicable time |
| --- | --- | --- | --- |
| Bitfinex | 3 | 2 cold; 1 hot | Self-declared labels in the pinned source; operating interval unspecified |
| Binance | 4 | all unknown | Reserve snapshot 2022-11-10 00:00 UTC; not a current ownership assertion |

All hardware_wallet and illicit_label values remain unknown. A first-party
publication supports a self-declared attribution; it is not a cryptographic proof
of ownership, control or operational security.

## Bitfinex evidence chain

The official Bitfinex announcement dated 2022-11-11 links to its public wallet list:
https://blog.bitfinex.com/announcements/bitfinex-resilient-in-face-of-market-events-committed-to-greater-transparency-and-demonstrating-proof-of-reserves/

The exact version reviewed is pinned:
https://github.com/bitfinexcom/pub/blob/83d06bdb5f5a2ce05d5ba2db5a426dd44c9f5128/wallets.txt

Its first three BTC entries distinguish one hot address and two cold addresses.
The source is independent of WalletExplorer's attribution process. Labels are
recorded as published, without extrapolating their validity across transaction
history. No hardware device is identified.

## Binance evidence

https://www.binance.com/en-IN/blog/community/2895840147147652626

Published 2022-11-10 and updated 2023-10-09. The BTC table provides four exact
addresses within a historical reserve snapshot. The surrounding text refers to
both hot and cold wallets but does not classify each row. Therefore only the
entity attribution is populated. Storage_source_url is empty and storage_type
remains unknown. Do not infer current ownership from this historical statement.

## Other sources screened

OKX describes its offline custody design at https://www.okx.com/en-eu/wallet-security
but that page does not bind the description to exact BTC addresses. No address
was imported from it. Crypto.com's PoR page and CEO announcement were checked;
the accessible first-party material did not yield an exact address-specific cold
label suitable for this batch. Neither absence implies lack of cold storage.

## Collection and next interpretation

The combined table is in ../results/research_seeds_20261005/results.csv.
Collection timestamps describe provider retrieval, not the dates of the input
claims. The historic one-address result directory remains an earlier experiment;
it uses its own saved input, not the expanded seed CSV.

Compare input entity_name against provider service_label while retaining unknown
and missing results. WalletExplorer does not validate storage_type. Next, expand
the cold/hot evidence across more entities before analysing dated activity.
