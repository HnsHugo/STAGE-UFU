# Task 2 — Wallet and transaction behaviour

## Research direction (provisional)

The supervisor's remembered keywords are WalletExplorer, hardware-wallet-related
addresses and CPFP flags. The exact scope and the intended meaning of cold vs
hardware wallets still need confirmation. This is a working plan, not an official
assignment or a claim that these behaviours identify illicit activity.

1. Address-to-cluster observations with WalletExplorer (first implementation).
2. Build a sourced cold/hardware-wallet dataset with explicit evidence levels.
3. Extract behavioural features and document competing explanations.
4. Investigate CPFP candidates and fees relative to contemporaneous conditions.
5. Test hypotheses against independently sourced licit/illicit labels.

A hardware wallet is a signing device; cold storage is an operational practice.
An address format does not establish either property. Keep service attribution,
storage classification and illicit labels as separate fields with separate sources.

## Current progress

Part 1 contains single-address and CSV collection CLIs, sourced input records,
real API snapshots and offline tests for validation, error handling and resume.
The seed table now includes seven first-party research addresses: three Bitfinex
addresses with published hot/cold labels and four historical Binance reserve
addresses with unknown storage. WalletExplorer found all seven but supplied no
service names. These are collection results, not illicit-correlation findings.
It queries an existing clustering service; it does not implement clustering itself.
No hardware/cold classification, CPFP detection or illicit classifier exists yet.

## Validation constraint

Task 1 uses the original anonymized Elliptic dataset. Its txId values are dataset
identifiers, not a supplied mapping to on-chain transaction hashes. We cannot join
new on-chain fee/CPFP measurements to those labels without a verified mapping.
Use Elliptic separately for graph/ML baselines and investigate a labeled on-chain
dataset for the new feature hypotheses before promising a correlation analysis.

Source: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set

## Expanded sample

The latest collection is Part 1/results/research_expanded_20261005/results.csv.
There are now 10 research addresses across Bitfinex, Binance and Change, plus one
smoke-test address. Five published cold labels span two entities; only one hot
address is available. Change's storage claim applies to a 2025-03-31 snapshot,
and does not establish an address-specific hardware model. All 11 lookups were
found, but none of the 10 research addresses received a provider service label.
Earlier dated result directories preserve earlier samples.

## First on-chain history collection

Part 1 now includes `collect_history.py`, using at most 25 recent confirmed
transactions per address in the initial run. All 11 addresses succeeded, yielding
206 address/transaction observations. Labels and provenance remain in
address_summary.csv, while transactions.csv supplies dated flows and transaction
fees. See Part 1/HISTORY.md for count-based coverage and non-atomic snapshot limits.
The 14 offline tests cover ingestion, response validation, pagination, amount
attribution, coverage changes and resumable collection. CPFP, holding-time and
illicit inference remain unimplemented.
