# Task 1 - Introduction to Blockchain Data Analysis

## Objective

The objective of this task is to understand how Bitcoin blockchain data is structured, how it can be retrieved, and how it can be prepared for further analysis.

This task currently covers:

- Bitcoin transaction structure
- UTXO model
- block explorers
- confirmed and candidate blocks
- mining pools
- addresses and entities
- change outputs
- Bitcoin data acquisition methods
- API-based transaction retrieval
- transaction fee calculation
- transaction weight and virtual size
- fee-rate analysis
- coinbase transactions
- JSON storage of raw and enriched transaction data

The general progression is:

```text
Understand blockchain data
        ↓
Inspect real transactions manually
        ↓
Retrieve them programmatically
        ↓
Extract useful features
        ↓
Prepare data for large-scale analysis
```

---

# Part 1 - Bitcoin Data Model and Block Explorers

## Bitcoin Data Model

Bitcoin uses the **UTXO model**.

UTXO means:

```text
Unspent Transaction Output
```

Unlike account-based systems, Bitcoin does not simply store a balance associated with each user. Instead, Bitcoin transactions consume previously created outputs and create new outputs.

General structure:

```text
Block
→ Transactions
→ Inputs / Outputs
→ UTXOs
→ Addresses / Scripts
```

A simplified transaction can be represented as:

```text
Previous UTXO
      ↓
    Input
      ↓
 Transaction
   ↓      ↓
Output  Output
   ↓      ↓
New UTXOs
```

## Transactions

A Bitcoin transaction consumes one or more previous UTXOs as inputs and creates one or more outputs.

Each transaction is identified by a unique identifier:

```text
txid
```

Important transaction information includes:

- transaction ID
- inputs
- outputs
- input values
- output values
- fees
- transaction size
- confirmation status
- block containing the transaction

## Inputs

An input references a previous output created by another transaction.

In a normal Bitcoin transaction, an input points to an existing UTXO.

Example:

```text
Previous transaction
        ↓
Output of 1 BTC
        ↓
Used as input in a new transaction
```

When this output is spent, it stops being an UTXO.

## Outputs

A transaction creates new outputs.

Each output contains:

- a value
- a locking script
- usually an address representation

If an output has not yet been spent, it is considered an UTXO.

Example:

```text
Transaction
   ↓
Output 0 → 0.6 BTC
Output 1 → 0.39 BTC
```

These outputs can later be used as inputs in future transactions.

## Bitcoin Balance and UTXOs

A Bitcoin balance can be understood as the sum of all UTXOs controlled by a given set of private keys.

Example:

```text
Address
  ↓
UTXO 1
UTXO 2
UTXO 3
...
  ↓
Sum = current spendable balance
```

An address with a balance of 30 BTC may therefore actually control many separate UTXOs whose total value is 30 BTC.

## Transaction Fees

For a normal Bitcoin transaction:

```text
Transaction fee = Total input value - Total output value
```

Example:

```text
Input:
1.00000000 BTC

Outputs:
0.60843700 BTC
0.39066300 BTC
```

The total output value is:

```text
0.60843700 + 0.39066300
= 0.99910000 BTC
```

Therefore:

```text
Fee
= 1.00000000 - 0.99910000
= 0.00090000 BTC
```

In satoshis:

```text
Input:
100000000 sats

Outputs:
60843700 sats
39066300 sats

Fee:
90000 sats
```

The fee is collected by the miner who includes the transaction in a block.

## Change Outputs

Bitcoin transactions consume complete UTXOs.

If the sender has an UTXO that is larger than the desired payment, the entire UTXO is used as input and the remaining value is usually returned to the sender through a new output called a **change output**.

Example:

```text
Input:
1 BTC

Outputs:
0.608 BTC → possible payment
0.390 BTC → possible change

Remaining difference → transaction fee
```

Another example:

```text
Input:
6.569 BTC

Outputs:
0.00198 BTC → possible payment
6.56572 BTC → possible change

Remaining difference → fee
```

Using a large UTXO for a small payment is therefore not necessarily a waste. It behaves somewhat like paying with a large banknote and receiving change.

However, the blockchain does not explicitly indicate which output is the payment and which output is the change. This must often be inferred using heuristics.

## Address vs User

An important concept in blockchain analysis is:

```text
Address ≠ User
```

A single person, wallet, exchange, company or other entity may control many different Bitcoin addresses.

Therefore:

```text
Address A → Address B
```

does not necessarily mean that two different people are involved.

This introduces important blockchain-analysis concepts such as:

- address clustering
- change-address heuristics
- entity identification

## Block Height

Each Bitcoin block has a position in the blockchain called the **block height**.

Example:

```text
Block 967010
Block 967011
Block 967012
```

## Block Timestamp

Bitcoin transactions do not contain their own consensus timestamp.

The time associated with a confirmed transaction generally comes from the timestamp of the block containing it.

## Block Explorers

Block explorers provide a human-readable interface for blockchain data.

Examples:

- mempool.space
- Blockstream Explorer

They make it possible to inspect:

- blocks
- transactions
- addresses
- inputs
- outputs
- UTXOs
- fees
- fee rates
- confirmations
- scripts
- mining pools

Block explorers are very useful for learning and manual investigation, but they are not suitable for large-scale analysis.

## Confirmed and Candidate Blocks

On mempool.space, confirmed blocks correspond to blocks that have already been mined and accepted by the Bitcoin network.

Candidate blocks represent groups of unconfirmed transactions currently present in the mempool. They are estimates of which transactions could be included in upcoming blocks.

```text
Unconfirmed transactions
        ↓
Candidate blocks
        ↓
-------------------
        ↓
Confirmed blocks
```

Candidate blocks are not yet part of the blockchain.

## Mining Pools

Mining pools combine the computing power of many miners.

Examples observed:

- Foundry USA
- AntPool
- F2Pool
- ViaBTC

Simplified process:

```text
Many miners
     ↓
Mining pool
     ↓
Combined hashrate
     ↓
Valid block found
     ↓
Block reward + transaction fees
     ↓
Reward distributed among pool participants
```

When a block explorer indicates that a block was mined by a specific pool, it means that the successful block was produced through that pool.

Mining pools mainly exist to make mining income more regular.

## Coinbase Transactions

Every Bitcoin block contains a special first transaction called the **coinbase transaction**.

A coinbase transaction:

- does not consume previous UTXOs
- creates the miner reward
- distributes the block subsidy and transaction fees

The miner reward contains:

```text
Block subsidy
+
Transaction fees from the block
```

At the current block subsidy:

```text
3.125 BTC
+
transaction fees
```

Because coinbase transactions do not use normal transaction inputs, the standard formula:

```text
Inputs - Outputs = Fee
```

does not apply.

Coinbase outputs also require a maturity period before they can be spent.

## Multisignature Addresses

Some Bitcoin outputs use multisignature scripts.

For example:

```text
2-of-3 multisignature
```

means that three public keys exist, but any two valid signatures are sufficient to spend the funds.

Example:

```text
Keys:
A
B
C

Valid:
A + B
A + C
B + C
```

One signature alone is not enough.

---

# Part 2 - Bitcoin Data Acquisition

## Objective

The objective of this part is to understand how Bitcoin data can be retrieved automatically and transformed into structured information that can later be used for large-scale analysis.

The general workflow is:

```text
Bitcoin blockchain
        ↓
Data acquisition
        ↓
Raw blockchain data
        ↓
Parsing / processing
        ↓
Structured dataset
        ↓
Analysis
```

## Data Acquisition Methods

The main methods studied are:

- block explorers
- blockchain APIs
- Bitcoin Core
- blockchain dumps
- public blockchain datasets
- Google BigQuery

## Block Explorers

Advantages:

- easy to use
- no setup required
- useful for manual investigation

Limitations:

- manual
- inefficient for many transactions
- not suitable for large-scale analysis

## Blockchain APIs

Blockchain APIs allow blockchain information to be retrieved automatically.

Typical data available includes:

- blocks
- transactions
- addresses
- inputs
- outputs
- fees
- confirmation status
- scripts

Advantages:

- easy to automate
- structured responses
- convenient for small experiments
- useful for scripts and prototypes

Limitations:

- API rate limits
- dependency on third-party services
- inefficient for very large datasets

## Bitcoin Core

Bitcoin Core is the reference Bitcoin client.

Running a full node makes it possible to download, verify and store the blockchain locally.

Raw blockchain data is stored in files such as:

```text
blk*.dat
```

Typical workflow:

```text
Bitcoin Network
      ↓
Bitcoin Core Full Node
      ↓
Raw blk*.dat files
      ↓
Parser
      ↓
Blocks / Transactions / Inputs / Outputs
      ↓
Database / CSV / Graph
```

Advantages:

- complete blockchain data
- independent from third-party APIs
- full control over the data
- suitable for research

Limitations:

- large storage requirements
- long synchronization time
- raw binary data must be parsed
- more complex setup

## Blockchain Dumps

Blockchain dumps are exported or preprocessed blockchain datasets.

They can be provided in formats such as:

- CSV
- JSON
- database files
- graph datasets

Advantages:

- easier to use than raw Bitcoin Core files
- quicker to start working with
- useful for research

Limitations:

- may not contain all blockchain information
- may already have undergone preprocessing
- format depends on the provider
- may not always be up to date

## Google BigQuery

Public blockchain datasets can be queried directly using SQL.

This makes it possible to analyze large amounts of blockchain data without downloading the full blockchain locally.

BigQuery will be studied in the next part.

## Method Comparison

| Method | Easy to use | Large-scale analysis | Full data |
|---|---|---|---|
| Block Explorer | Yes | No | No |
| API | Yes | Limited | Usually no |
| Bitcoin Core | No | Yes | Yes |
| Blockchain Dump | Medium | Yes | Depends |
| BigQuery | Yes | Yes | Large public dataset |

## Practical Experiment with the Blockstream API

A Python script was created to retrieve real Bitcoin transactions using the Blockstream API.

The script sends a request using the transaction ID:

```text
https://blockstream.info/api/tx/{txid}
```

The API returns structured transaction data in JSON format.

The raw response contains information about:

- inputs
- outputs
- scripts
- previous outputs
- transaction size
- weight
- confirmation status
- block information

## Python Transaction Analysis Script

The Python script automatically:

- retrieves a transaction using its TXID
- detects whether it is a normal or coinbase transaction
- counts inputs and outputs
- extracts input and output addresses
- calculates total input value
- calculates total output value
- calculates transaction fees
- retrieves transaction weight
- calculates virtual size
- calculates fee rate
- assigns a simple fee-rate category
- saves raw and processed data as JSON

## Fee Calculation

For normal Bitcoin transactions:

```text
Fee = Total input value - Total output value
```

Example:

```text
Input:
1 BTC

Outputs:
0.608437 BTC
0.390663 BTC

Fee:
0.000900 BTC
```

or:

```text
90000 sats
```

## Satoshis

Bitcoin values are commonly represented in satoshis:

```text
1 BTC = 100,000,000 satoshis
```

Using satoshis is useful because transaction values are represented as integers.

## Transaction Weight

Bitcoin uses transaction weight to account for SegWit data.

Weight is expressed in:

```text
Weight Units (WU)
```

## Virtual Size

Virtual size is calculated as:

```text
vsize = ceil(weight / 4)
```

and is expressed in virtual bytes:

```text
vB
```

Example:

```text
weight = 560 WU
vsize = 140 vB
```

## Fee Rate

The fee rate is:

```text
Fee rate = Fee / Virtual size
```

and is expressed in:

```text
sat/vB
```

Example:

```text
Fee = 15820 sats
Virtual size = 140 vB

Fee rate = 113 sat/vB
```

## Why Fee Rate Matters

The amount of BTC transferred is not the main factor determining transaction fees.

Miners mainly evaluate the fee relative to transaction size.

Therefore, a transaction sending `0.001 BTC` and another sending `100 BTC` may pay similar fees if their virtual sizes are similar.

## Simple Fee Classification

A simple local classification was implemented:

```text
< 5 sat/vB      → low
< 20 sat/vB     → normal
< 100 sat/vB    → high
>= 100 sat/vB   → very high
```

This classification is intentionally simple and is used only as an analytical feature.

## Limitation of Static Fee Categories

A fee rate cannot truly be considered high or low without considering the state of the network.

For example, `100 sat/vB` may be excessive during low congestion but normal during a highly congested period.

A better analysis would compare:

```text
Transaction fee rate
        ↓
Mempool fee rate at the same time
        ↓
Relative fee level
```

## Fee Overpayment

Some analyzed transactions showed very high fee rates compared with surrounding network conditions.

Observed examples included approximately:

```text
113 sat/vB
```

and:

```text
913 sat/vB
```

Possible explanations include:

- manually selected fee rate
- badly configured wallet
- incorrect fee estimation
- automated service behavior
- urgent confirmation preference
- fee bumping mechanisms
- unusual transaction behavior

Such values may later become useful features for anomaly detection.

## CPFP

A transaction can use:

```text
Child Pays For Parent (CPFP)
```

A child transaction may pay a high fee so that miners have an incentive to include both the child and a low-fee parent transaction.

Therefore, a high transaction fee does not always indicate an error.

## RBF

Bitcoin transactions may also support:

```text
Replace By Fee (RBF)
```

RBF allows an unconfirmed transaction to be replaced by another version paying a higher fee.

RBF and CPFP are relevant when studying transaction fee behavior.

## Experimental Transactions

Five real Bitcoin transactions were selected and analyzed:

- 2 transactions with very high fee rates
- 1 transaction with a high fee rate
- 1 transaction with a low fee rate
- 1 coinbase transaction

These examples provide several different transaction behaviors.

## Coinbase Handling in the Script

Coinbase transactions require special handling because they do not consume normal previous UTXOs.

The script detects coinbase transactions separately and avoids applying the standard fee formula to them.

## JSON Storage

Each analyzed transaction is saved as a separate JSON file.

Example structure:

```text
Task1/
├── README.md
├── fetch_transaction.py
└── transactions/
    ├── transaction_1.json
    ├── transaction_2.json
    ├── transaction_3.json
    ├── transaction_4.json
    └── transaction_5.json
```

In practice, the transaction ID can be used as the filename:

```text
transactions/
└── b2f9821e8f151250....json
```

This prevents previous transactions from being overwritten.

## Raw Data and Analysis

Each JSON file contains two main sections:

```json
{
  "raw_transaction": {},
  "analysis": {}
}
```

### raw_transaction

Contains the original response returned by the Blockstream API.

### analysis

Contains calculated features such as:

- transaction ID
- coinbase status
- number of inputs
- number of outputs
- total input value
- total output value
- transaction fee
- transaction weight
- virtual size
- fee rate
- fee classification

## Why Preserve Raw Data?

Keeping raw data separate from calculated features is useful because:

- the original information remains available
- calculated fields can be changed later
- new features can be added without downloading the transaction again
- processing errors can be checked against the original source

The workflow becomes:

```text
API
 ↓
Raw transaction
 ↓
Feature extraction
 ↓
Analysis data
```

## Feature Engineering

The script already introduces feature engineering by transforming raw blockchain information into variables such as:

```text
number_of_inputs
number_of_outputs
input_value
output_value
fee
weight
vsize
fee_rate
coinbase_status
```

Later, additional features could include:

```text
fee_rate_vs_network
confirmation_delay
address_reuse
change_output_probability
number_of_previous_transactions
```

These features could be used for:

- statistics
- clustering
- machine learning
- graph analysis
- anomaly detection

## Current Data Processing Pipeline

```text
Bitcoin blockchain
        ↓
Block explorer
        ↓
Manual inspection
        ↓
Blockstream API
        ↓
Raw JSON
        ↓
Python script
        ↓
Feature extraction
        ↓
Enriched JSON
        ↓
Future large-scale analysis
```

---

# Current Progress

Completed:

- Bitcoin transaction structure
- UTXO model
- transaction inputs and outputs
- transaction fee calculation
- block explorer usage
- confirmed and candidate block understanding
- mining pool understanding
- address and entity distinction
- change-output concept
- coinbase transaction understanding
- Bitcoin data acquisition methods
- Blockstream API usage
- Python-based transaction retrieval
- transaction JSON storage
- raw and enriched data separation
- transaction weight analysis
- virtual-size calculation
- fee-rate calculation
- fee-rate classification
- basic fee anomaly observations
- analysis of five real Bitcoin transactions

---

# Part 3 - Large-Scale Bitcoin Analysis with Google BigQuery

## Objective

The objective of this part is to move from individual transaction analysis to large-scale Bitcoin analysis using Google BigQuery.

Dataset used:

```text
bigquery-public-data.crypto_bitcoin.transactions
```

BigQuery makes it possible to query millions of Bitcoin transactions directly with SQL without downloading the full blockchain locally.

---

## Dataset Structure

The `transactions` table contains fields such as:

```text
hash
block_timestamp
block_number
input_count
output_count
input_value
output_value
fee
size
virtual_size
is_coinbase
inputs
outputs
```

The table is partitioned by:

```text
block_timestamp_month
```

Using this field is important to reduce the amount of data scanned.

Example:

```sql
WHERE block_timestamp_month = DATE('2026-09-01')
```

---

## Query Organization

Each query is stored in a separate `.sql` file and linked to a CSV result.

```text
part3/
├── queries/
│   ├── q01_sample_transactions.sql
│   ├── q02_highest_fee_rates.sql
│   ├── q03_fee_statistics.sql
│   ├── q04_transactions_per_day.sql
│   ├── q05_daily_transaction_statistics.sql
│   └── q06_largest_transactions.sql
│
└── results/
    ├── q01_sample_transactions.csv
    ├── q02_highest_fee_rates.csv
    ├── q03_fee_statistics.csv
    ├── q04_transactions_per_day.csv
    ├── q05_daily_transaction_statistics.csv
    └── q06_largest_transactions.csv
```

---

## Q01 - Sample Transactions

The first query retrieves a small sample of Bitcoin transactions.

It was used to inspect the schema and compare BigQuery data with the transaction analysis performed in Part 2.

Example fields retrieved:

- TXID
- timestamp
- block number
- input count
- output count
- input value
- output value
- fee
- virtual size
- coinbase status

---

## Q02 - Highest Fee Rates

The second query searches for transactions with the highest fee rates.

Fee rate is calculated as:

```text
fee_rate = fee / virtual_size
```

Several extreme cases were found, including transactions above:

```text
20,000 sat/vB
```

These transactions are strong statistical outliers, although a high fee does not automatically mean an error.

Possible explanations include:

- manual fee settings
- wallet misconfiguration
- automated systems
- RBF
- CPFP
- unusual transaction behavior

---

## Q03 - Fee Statistics

Fee-rate statistics were calculated over millions of transactions.

Approximate results:

```text
Average:  ~1.60 sat/vB
Median:   ~0.35 sat/vB
P90:      ~3.92 sat/vB
P95:      ~5.00 sat/vB
P99:      ~12.15 sat/vB
Maximum:  >22,000 sat/vB
```

The distribution is highly skewed, with a small number of transactions paying much larger fee rates than normal.

This confirmed that the highest-fee transactions were real outliers.

---

## Q04 - Transactions per Day

Bitcoin transaction activity was aggregated by day.

Daily activity was generally in the range of several hundred thousand transactions, with some days approaching:

```text
900,000 transactions
```

The most recent day in the dataset may be incomplete because the query can be executed before the end of the UTC day.

---

## Q05 - Daily Transaction Statistics

Daily statistics were calculated for:

- transaction count
- average input value
- average output value
- average fee
- average fee rate

One important observation is:

```text
More transactions
≠
Automatically higher fees
```

Transaction fees depend more on competition for block space and transaction structure than on transaction count alone.

---

## Q06 - Largest Transactions

The largest transactions were selected using total input value.

Some transactions moved close to:

```text
50,000 BTC
```

However, a very large `input_value` does not necessarily represent a large payment.

Inspection of these transactions showed that they can represent:

- internal wallet transfers
- exchange movements
- UTXO consolidation
- wallet sweeps
- cold-storage management

Therefore:

```text
High on-chain transaction value
≠
High economic payment
```

Blockchain data shows how coins move, but not the real-world intent behind every transaction.

---

## Query Cost

BigQuery queries are billed mainly according to the amount of data scanned.

For example:

```sql
LIMIT 20
```

does not necessarily mean that only 20 rows are read.

Some queries processed more than 100 GB because BigQuery still had to scan and sort a large monthly partition.

Useful practices include:

- filtering by partition
- selecting only necessary columns
- avoiding `SELECT *`
- avoiding unnecessary nested fields
- checking the estimated query size before execution

---

## Main Lessons

This part demonstrated how to:

- access Bitcoin public data with BigQuery
- inspect a large blockchain dataset
- query millions of transactions with SQL
- use partition filtering
- calculate fee rates
- calculate statistical distributions
- aggregate blockchain activity by day
- identify extreme transactions
- analyze very large value transfers
- export SQL results to CSV

The main transition from Part 2 to Part 3 is:

```text
Part 2:
Single transaction
→ API
→ Python analysis

Part 3:
Millions of transactions
→ SQL
→ Large-scale analysis
```

---

## Part 4 - Elliptic Bitcoin Dataset

### Objective

The objective of this part was to explore the Elliptic Bitcoin Dataset and perform an initial graph-based analysis of Bitcoin transactions.

The dataset was downloaded from Kaggle and contains transaction features, transaction labels and transaction relationships.

### Dataset

The Elliptic dataset contains:

- 203,769 transactions
- 234,355 directed edges
- 166 features per transaction
- 49 time steps

Transaction labels are defined as:

- `1` - illicit
- `2` - licit
- `unknown` - unlabeled transaction

The class distribution is highly imbalanced:

- Unknown: 157,205 transactions
- Licit: 42,019 transactions
- Illicit: 4,545 transactions

Among labeled transactions, approximately 90% are licit and 10% are illicit.

### Graph Construction

A directed transaction graph was constructed using NetworkX.

Each node represents a Bitcoin transaction and each directed edge represents a flow between two transactions.

The transaction labels were added as node attributes in order to compare the graph characteristics of licit and illicit transactions.

### Graph Analysis

Basic graph statistics were computed, including:

- number of nodes
- number of edges
- average in-degree
- average out-degree
- maximum in-degree
- maximum out-degree

The average degree values show differences between licit and illicit transactions.

Licit transactions:

- Average in-degree: 1.9094
- Average out-degree: 1.1858

Illicit transactions:

- Average in-degree: 1.2700
- Average out-degree: 0.7417

### Degree Distribution

The degree distributions were also compared using the mean, median, 90th percentile and maximum values.

For licit transactions:

- Total degree mean: 3.0952
- Median: 2
- 90th percentile: 4
- Maximum: 473

For illicit transactions:

- Total degree mean: 2.0117
- Median: 1
- 90th percentile: 2
- Maximum: 177

The results show that, in this dataset, labeled licit transactions tend to be more connected than labeled illicit transactions.

However, these observations are specific to the Elliptic dataset and should not be interpreted as a general property of illicit Bitcoin transactions.

### Conclusion

This part provided a first practical introduction to blockchain graph analysis.

The main steps were:

1. Load the Elliptic dataset
2. Analyze the class distribution
3. Construct the Bitcoin transaction graph
4. Associate transaction labels with graph nodes
5. Compare graph properties of licit and illicit transactions

This analysis provides the foundation for future work involving machine learning, Graph Neural Networks and anomaly detection.