# Seed address table

`seed_addresses.csv` is the input list for future collection. One row represents
one public Bitcoin mainnet address, not a wallet, person or transaction.
Current state: one API smoke-test address, zero independently verified storage or
illicit labels. The single-address CLI does not read this CSV yet.

## Columns

| Column | Definition |
| --- | --- |
| address | Public Bitcoin address; preserve as text |
| network | Currently bitcoin_mainnet |
| purpose | api_smoke_test or research_sample |
| entity_name | Attributed entity name, or unknown |
| entity_source_url | Evidence supporting the entity attribution |
| entity_evidence | unknown, provider_attribution, first_party_publication or controlled_experiment |
| storage_type | unknown, hot or cold; describes operational storage |
| storage_source_url | Evidence explicitly supporting hot/cold classification |
| hardware_wallet | unknown or documented device/model; separate from hot/cold |
| hardware_source_url | Evidence supporting actual hardware use |
| illicit_label | unknown, licit or illicit; requires a defined, sourced label |
| illicit_source_url | Evidence and context supporting that label |
| reviewed_at_utc | UTC time when this record's evidence was reviewed |
| notes | Scope, limitations, dates of applicability or experiment details |

## Entry rules

- UTF-8 CSV with commas. Unknown categorical facts use `unknown`; absent source
  URLs are empty. Never replace unknown with false, licit or hot.
- Maintain one row per address/network. Conflicting evidence stays unknown until
  reviewed; explain it in notes. Split to a dated evidence table if history grows.
- Every positive attribution needs its corresponding source. The evidence must
  name the exact address or document how the experiment produced it.
- Record the claim's applicable period in notes. Review time is not ownership time.
- A service label does not establish storage practice, hardware usage or legality.
- Only public addresses are stored. Seeds, private keys and XPUBs are not needed.
- Provider attribution is not independent validation of that provider's results.
  Exclude api_smoke_test rows from later research comparisons.
- Hardware-generated addresses without transactions can test address generation,
  but cannot supply on-chain behaviour or CPFP examples.
- An illicit label must specify what is being labeled, why, and for which period.
  An exchange name, missing label or high fee cannot supply this classification.

## First row

The address comes from the official WalletExplorer API example:
https://www.walletexplorer.com/api

The BTC-e.com attribution is from the captured API response, not an independent
ownership claim. Its retrieval date and indexed height remain available in
`../results/api_example_snapshot.json`. All storage/hardware/illicit fields are
unknown. This record tests the collection workflow only.

## Next collection step

Implement CSV ingestion and validation, then query WalletExplorer for each unique
address with bounded requests. Keep provider outputs in dated results rather than
overwriting the input evidence. Add independent research addresses after reviewing
first-party publications or a documented controlled experiment.
