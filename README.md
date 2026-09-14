# Task 1 - Part 1: Bitcoin Data Model & Block Explorers

## Bitcoin data model

Bitcoin does not use an account-based model like Ethereum.
It uses the UTXO model.

Main structure:

Block
→ Transactions
→ Inputs / Outputs
→ UTXOs
→ Addresses / Scripts

A transaction consumes previous unspent outputs as inputs
and creates new outputs.

Important concepts:
- txid: unique transaction identifier
- input: references a previous UTXO
- output: creates a new UTXO
- value: amount of BTC transferred
- fee: difference between total input value and total output value
- block height: position of the block in the blockchain
- timestamp: time associated with the block
- coinbase transaction: first transaction in a block, used to reward the miner

## Block explorers

A block explorer is a tool used to inspect blockchain data.

Examples:
- mempool.space
- Blockstream Explorer

With a block explorer, we can inspect:
- blocks
- transactions
- addresses
- inputs and outputs
- fees
- confirmation status
- transaction size / weight

A block explorer is useful for manual analysis, but it is not suitable for large-scale analysis.
For larger datasets, APIs, blockchain dumps, Bitcoin Core or BigQuery are more appropriate.

# Task 1 - Part 2: Bitcoin Data Acquisition

## Overview

There are several ways to obtain Bitcoin blockchain data.

Main methods:

- Block explorers
- APIs
- Bitcoin Core
- Blockchain dumps
- Public datasets such as Google BigQuery

Each method is useful depending on the scale of the analysis.

## Block explorer APIs

Instead of manually browsing transactions, APIs allow us to retrieve blockchain data automatically.

Typical data available through an API:
- blocks
- transactions
- addresses
- inputs and outputs
- fees
- confirmations

Advantages:
- easy to use
- quick to start
- good for small experiments

Limitations:
- rate limits
- dependency on an external service
- not ideal for very large-scale analysis

## Bitcoin Core

Bitcoin Core is the reference Bitcoin client.

A full node downloads and verifies the Bitcoin blockchain.

The blockchain is stored locally in files such as:

`blk*.dat`

These files contain raw block data.

General workflow:

Bitcoin Network  
→ Bitcoin Core Full Node  
→ Raw block files  
→ Parser  
→ Transactions / Inputs / Outputs  
→ Database / CSV / Graph

Advantages:
- complete blockchain data
- independent from third-party APIs
- suitable for serious research

Limitations:
- large storage requirements
- long synchronization time
- raw data must be parsed before analysis

## Blockchain dumps

A blockchain dump is an exported version of blockchain data.

Instead of running a full node, researchers can use preprocessed datasets containing:
- transactions
- addresses
- inputs
- outputs
- block information

The data may be stored as:
- CSV
- JSON
- database files
- graph datasets

Advantages:
- easier to process than raw blockchain files
- faster to start research

Limitations:
- may not contain all blockchain information
- format depends on the provider
- dataset may not be up to date

## Comparison

| Method | Easy to use | Large-scale analysis | Full data |
|---|---|---|---|
| Block Explorer | Yes | No | No |
| API | Yes | Limited | Usually no |
| Bitcoin Core | No | Yes | Yes |
| Blockchain Dump | Medium | Yes | Depends on dataset |
| BigQuery | Yes | Yes | Large public dataset |

## Key idea

For small tests, APIs and block explorers are sufficient.

For large-scale blockchain analysis, researchers usually use:

- Bitcoin Core
- blockchain dumps
- databases
- BigQuery

The objective is to transform raw blockchain data into structured datasets that can later be used for statistics, clustering, machine learning and graph analysis.