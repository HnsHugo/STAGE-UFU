# Data selected for the next experiment

## Two distinct objectives

1. Learn to train and evaluate an address model: the Elliptic++ benchmark.
2. Detect addresses receiving/holding stolen funds: a corpus of documented cases, still insufficient for reliable supervised classification.

Elliptic++ “illicit” labels do not mean “stolen funds.” These corpora must not be merged without a shared definition of the target and features.

## Elliptic++: selected educational benchmark

Authors' source: https://github.com/git-disl/EllipticPlusPlus
Publication: https://arxiv.org/abs/2306.06108
Inspected revision: `08fe6aded83afb97bf5a79a71130f542ca783c2e`.

The class file was downloaded and its SHA-256 verified. Actual counts:

| Original class | Meaning supplied by the authors | Addresses |
| --- | --- | ---: |
| 1 | Illicit | 14 266 |
| 2 | Licit | 251 088 |
| 3 | Unknown | 557 588 |

Total: 822 942 distinct addresses, zero duplicates in the class file. The 265 354 addresses labeled 1/2 can support the supervised benchmark. Unknowns are excluded from its binary evaluation, not converted into licit examples.

Original files:

- `wallets_classes.csv`: 30 421 134 bytes, SHA-256 `4e5132c99f941666bf1fefd4100a1428d339c9252ec6987909e1adf8eac902f9`.
- `wallets_features.csv`: 606 463 522 bytes reported by the Git LFS pointer, expected SHA-256 `317daca2810c355ddfdb8c0dab34cf11d1aa90567fe975090c7e5a901386eb77`.

The feature header was actually read: address, time step, sending/receiving activity, amounts, fees, block intervals, etc. At the time of the initial source selection, the complete feature file had not yet been downloaded or audited. The subsequent completed audit and benchmark are documented in [../ellipticplusplus/README.md](../../supplementary/ellipticplusplus/README.md). The repository provides educational classification and visualization notebooks.

Reproducible download with checksum verification:

```bash
python download_ellipticplusplus.py /tmp/ellipticplusplus
```

Do not add large CSV files to Git. Downloads are pinned to the inspected revision. Public availability does not by itself authorize commercial redistribution: examine the authors' terms before reuse in the future V2.

## Proposed training / validation / test split

To be confirmed after auditing the feature file:

- An address must appear in only one set, even if it has several temporal rows.
- Use training to learn rules, validation to select parameters, and retain the test set for final evaluation.
- An initial address-level, class-stratified split (60/20/20) serves as an educational reference.
- This split does not establish independence between entities or cases.
- A separate temporal test is useful only after checking that features do not summarize future events; total-lifetime and last-appearance columns need particular attention.
- Do not directly compare benchmark scores with Coldcard proxy scores: the target and observation unit change.

This was the proposed protocol at source-selection time. Address-disjoint training/validation/test sets have since been materialized and evaluated; see [the completed benchmark](../../supplementary/ellipticplusplus/README.md) for the actual protocol and results.

## Theft corpus: external references

### FBI group, August 2023

Six addresses and 22 distinct transactions have already been collected and checked against Blockstream counters. Source and results: `theft_seed_registry_20261010.json` and `theft_history_20261010/`.

Role: stolen-funds holders attributed by the FBI, not victim addresses. One reference group aggregating several thefts, not six independent cases.

### Binance, May 2019: new case reserved for external examination

Primary source: https://www.binance.com/en/support/announcement/detail/360028031711
Binance publishes the transaction:
`e8b406091959700dbffcff30a60b190133721e5c39e89bb5fe23c5a554ab05ea`.

The transaction was downloaded from Blockstream and saved in `external_cases/binance_2019_transaction.json` with its block reference. The response contains 71 inputs and 44 outputs. Do not label all outputs as stolen: the release identifies a transaction, not each output's role. This case is reserved as an exploratory external case before any training. Documented output attribution is still required for an address-level test.

### Bitfinex, August 2016: lead requiring further work

Primary sources:

- https://www.justice.gov/archives/opa/pr/bitfinex-hacker-and-wife-plead-guilty-money-laundering-conspiracy-involving-billions
- https://www.justice.gov/d9/press-releases/attachments/2022/02/08/statement_of_facts_pacer.pdf

The case is documented, but the court filing uses, among other identifiers, the cluster prefix “1CGA4s.” A prefix or cluster is insufficient to establish a list of complete addresses. No address is added on this basis alone.

## Remaining limitations for the stolen-funds objective

Additional cases with verifiable address roles, harmonized observation periods and an appropriate comparison group are still missing. No report does not constitute evidence of legitimacy. Elliptic++ allows progress in ML while this corpus is assembled, but does not validate a stolen-bitcoin or hardware-wallet detector.
