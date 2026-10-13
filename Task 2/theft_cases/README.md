# Sourced theft cases and decision-time features

## Current deliverables

- fbi_asof_20230823.json: six historical address profiles with source roles and a shared cutoff.
- binance_output_candidates.json: 44 outputs from the transaction published by Binance; one role is research-attributed through a unique match, and 43 remain unknown. See BINANCE_EVIDENCE.md.
- extract_asof_features.py: reproducible cutoff/window feature extraction from audited provider histories.
- Four tests cover future-spending exclusion, window boundaries, incoming-fee separation and pre-window balance.

## FBI historical snapshot

Source: https://www.fbi.gov/news/press-releases/fbi-identifies-cryptocurrency-funds-stolen-by-dprk
The six addresses are reported stolen-funds holders, not victims. The source aggregates several heists; all addresses remain in one case group. Hardware control and originating heist per address remain unknown.

Cutoff: 2023-08-23T00:00:00Z exclusive. Window: 2023-08-16T00:00:00Z inclusive to cutoff. The cutoff is a retrospective end-of-publication-day convention, not the exact publication timestamp or a verified operational decision time. All twelve transactions in the window are receipts; later transactions, including spending in 2024, are excluded.

Features include transaction counts, amounts received, own input amounts spent, net flows, balance before cutoff reconstructed from earlier transactions, receipt amounts, active UTC days, fixed-window activity rate and outgoing whole-transaction fee rates. With no outgoing transactions, outgoing fee-rate statistics remain null, not zero. Incoming transaction fees do not describe the receiving address owner's policy. Amount spent from own inputs is not a measure of external payments; change and self-transfers require further interpretation.

Transactions are filtered by provider block timestamps. These timestamps do not establish precise network arrival time and may be non-monotonic. Histories are checked against their saved manifest and file hashes, whose earlier collection was provider-count consistent; this is not cryptographic inclusion verification or independent provider agreement. Current UTXO/spending-status fields and post-cutoff transactions are not predictive inputs.

The feature schema differs from Elliptic++'s aggregate profiles. No forest score is produced and the Elliptic++ model must not be directly applied without verified feature compatibility and a suitable target.

## Binance case

Source: https://www.binance.com/en/support/announcement/detail/360028031711
The published transaction is e8b406091959700dbffcff30a60b190133721e5c39e89bb5fe23c5a554ab05ea.
Its saved API response has 71 inputs and 44 outputs. Each output is stored as a candidate with its index, address and amount. The incident-level statement does not establish each output's role. No output is labeled stolen or legitimate solely because it appears in this transaction. One candidate history has since been collected and checked; see BINANCE_EVIDENCE.md.

## Reproduction

From Task 2/theft_cases, use a new output filename:

```bash
python extract_asof_features.py ../coldcard/theft_history_20261010 ../coldcard/theft_seed_registry_20261010.json 2023-08-23T00:00:00Z new_fbi_snapshot.json --days 7
python -m unittest discover -p 'test_*.py' -v
```

## Remaining data requirements

The initial snapshot has six source-attributed positive-role examples in one group. The subsequent Binance evidence adds one research-attributed address in a second incident group; this remains insufficient for a supervised train/test dataset. There are no documented negative controls in this corpus. One Binance output is research-attributed; the other 43 remain unresolved. Additional independent cases, exact address-role evidence, label availability dates and matched comparison observations are required before theft-specific fitting or evaluation.

DMM and Bitfinex incident sources were screened, but the inspected material did not establish an importable complete-address list with sufficiently specific roles. No addresses were inferred from shortened prefixes, diagrams or incident amounts alone.

Next work: resolve output roles using explicit source evidence, collect compatible historical observations for additional cases and documented comparison groups, then establish case-disjoint evaluation. Missing reports remain unknown, never automatic legitimate labels.
