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

The objective of this part is to move from the analysis of individual Bitcoin transactions to the analysis of millions of transactions using **Google BigQuery** and the Bitcoin public dataset.

The dataset used is:

```text
bigquery-public-data.crypto_bitcoin

The main table used is:

bigquery-public-data.crypto_bitcoin.transactions

BigQuery makes it possible to perform large-scale blockchain analysis directly with SQL without downloading and storing the complete Bitcoin blockchain locally.

The general workflow is:

Bitcoin blockchain
        ↓
Google public dataset
        ↓
BigQuery SQL queries
        ↓
Filtered / aggregated results
        ↓
CSV export
        ↓
Further analysis
1. BigQuery Transaction Schema

The transactions table contains information such as:

hash
size
virtual_size
version
lock_time
block_hash
block_number
block_timestamp
block_timestamp_month
input_count
output_count
input_value
output_value
is_coinbase
fee
inputs
outputs

The inputs and outputs fields are nested structures containing more detailed transaction information.

This dataset therefore provides both high-level transaction features and detailed input/output data.

2. Partitioning and Query Cost

The Bitcoin transaction table contains a very large amount of data.

A first query using:

SELECT *
FROM `bigquery-public-data.crypto_bitcoin.transactions`
LIMIT 10;

would have processed approximately:

2.33 TB

This happens because LIMIT only limits the number of returned rows. It does not necessarily reduce the amount of data BigQuery must scan.

Therefore, queries should:

select only useful columns
use the partition column
avoid SELECT *
avoid reading large nested fields unnecessarily

The dataset is partitioned using:

block_timestamp_month

For example:

WHERE block_timestamp_month = DATE('2026-09-01')

allows BigQuery to scan only the September 2026 partition instead of the complete Bitcoin dataset.

This substantially reduces query cost.

3. Time Representation

The block_timestamp field uses UTC.

Therefore:

DATE(block_timestamp)

groups transactions according to UTC days.

For example, in Uberlândia:

12:00 local time (UTC-3)
=
15:00 UTC

This is important when analyzing an incomplete current day.

The most recent day in a query may contain only partial data and should therefore not be directly compared with complete previous days.

BigQuery Experiments

Each SQL query is stored separately and associated with a CSV result.

Project structure:

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

The same query number is used for the SQL file and its corresponding result.

Example:

q03_fee_statistics.sql
        ↕
q03_fee_statistics.csv
4. Q01 - Sample Transactions

The first query retrieves a small sample of transactions from September 2026.

SELECT
  `hash` AS txid,
  block_timestamp,
  block_number,
  input_count,
  output_count,
  input_value,
  output_value,
  fee,
  size,
  virtual_size,
  is_coinbase
FROM `bigquery-public-data.crypto_bitcoin.transactions`
WHERE block_timestamp_month = DATE('2026-09-01')
LIMIT 10;
Purpose

This query was used to:

understand the table structure
inspect real transaction values
verify available columns
compare BigQuery data with the transaction analysis performed in Part 2

The query processed approximately:

1.26 GB

instead of several terabytes after filtering the partition and selecting only useful columns.

5. Q02 - Transactions with the Highest Fee Rates

The second query searches for transactions with the highest fee rate.

SELECT
  `hash` AS txid,
  block_timestamp,
  block_number,
  input_count,
  output_count,
  input_value,
  output_value,
  fee,
  virtual_size,
  SAFE_DIVIDE(fee, virtual_size) AS fee_rate_sat_vb
FROM `bigquery-public-data.crypto_bitcoin.transactions`
WHERE block_timestamp_month = DATE('2026-09-01')
  AND is_coinbase = FALSE
  AND virtual_size > 0
ORDER BY fee_rate_sat_vb DESC
LIMIT 20;

The fee rate is calculated using:

fee_rate = fee / virtual_size
Observation

Several extremely high fee-rate transactions were found.

The highest observed transaction had a fee rate of approximately:

22,172 sat/vB

One example contained approximately:

Input value:
2,567,346 sats

Output value:
128,354 sats

Fee:
2,438,992 sats

This means that approximately 95% of the input value was used as transaction fees.

Inspection with mempool.space showed a fee rate above:

22,000 sat/vB

and confirmation within only a few seconds.

Such transactions may result from:

manual fee configuration
wallet misconfiguration
automated systems
unusual transaction behavior
fee bumping mechanisms
RBF
CPFP

A very high fee rate does not automatically mean that an error occurred, but it can be considered an interesting anomaly for further investigation.

6. Q03 - Fee-Rate Statistics

Instead of analyzing only extreme transactions, statistics were calculated for all normal Bitcoin transactions in the September partition.

WITH tx AS (
  SELECT
    fee,
    virtual_size,
    SAFE_DIVIDE(fee, virtual_size) AS fee_rate_sat_vb
  FROM `bigquery-public-data.crypto_bitcoin.transactions`
  WHERE block_timestamp_month = DATE('2026-09-01')
    AND is_coinbase = FALSE
    AND virtual_size > 0
)

SELECT
  COUNT(*) AS transaction_count,
  AVG(fee_rate_sat_vb) AS avg_fee_rate_sat_vb,
  MIN(fee_rate_sat_vb) AS min_fee_rate_sat_vb,
  MAX(fee_rate_sat_vb) AS max_fee_rate_sat_vb,

  APPROX_QUANTILES(fee_rate_sat_vb, 100)[OFFSET(50)]
    AS median_fee_rate_sat_vb,

  APPROX_QUANTILES(fee_rate_sat_vb, 100)[OFFSET(90)]
    AS p90_fee_rate_sat_vb,

  APPROX_QUANTILES(fee_rate_sat_vb, 100)[OFFSET(95)]
    AS p95_fee_rate_sat_vb,

  APPROX_QUANTILES(fee_rate_sat_vb, 100)[OFFSET(99)]
    AS p99_fee_rate_sat_vb

FROM tx;
Results

Approximately:

7,938,849 transactions

were included in the analysis.

The fee-rate distribution was approximately:

Average:  1.60 sat/vB
Median:   0.35 sat/vB
P90:      3.92 sat/vB
P95:      5.00 sat/vB
P99:     12.15 sat/vB
Maximum: ~22,172.65 sat/vB
Interpretation

The distribution is strongly skewed.

The median transaction paid only approximately:

0.35 sat/vB

while the maximum was above:

22,000 sat/vB

The highest transaction was therefore approximately:

~1,800 × P99

and tens of thousands of times larger than the median fee rate.

This confirms that the highest-fee transactions are statistical outliers rather than simply normal high-fee transactions.

However, fee analysis was not pursued further because the main objective of Task 1 is data acquisition and exploration rather than a complete study of Bitcoin transaction fees.

7. Q04 - Transactions per Day

The fourth query aggregates transaction activity by day.

SELECT
  DATE(block_timestamp) AS day,
  COUNT(*) AS transaction_count
FROM `bigquery-public-data.crypto_bitcoin.transactions`
WHERE block_timestamp_month = DATE('2026-09-01')
GROUP BY day
ORDER BY day;
Purpose

This query demonstrates how BigQuery can aggregate millions of Bitcoin transactions using a simple SQL query.

It also provides an overview of Bitcoin network activity over time.

Daily transaction volumes were generally in the range of several hundred thousand transactions.

A peak of close to:

900,000 transactions/day

was observed during the studied period.

The most recent day contained partial data because the query was executed before the end of the UTC day.

8. Q05 - Daily Transaction Statistics

The fifth query computes daily transaction statistics.

SELECT
  DATE(block_timestamp) AS day,
  COUNT(*) AS transaction_count,
  AVG(input_value) AS avg_input_value_sats,
  AVG(output_value) AS avg_output_value_sats,
  AVG(fee) AS avg_fee_sats,
  AVG(SAFE_DIVIDE(fee, virtual_size)) AS avg_fee_rate_sat_vb
FROM `bigquery-public-data.crypto_bitcoin.transactions`
WHERE block_timestamp_month = DATE('2026-09-01')
  AND is_coinbase = FALSE
  AND virtual_size > 0
GROUP BY day
ORDER BY day;
Observation

Daily transaction volume and daily fee rates do not necessarily move together.

A day with a very large number of transactions can still have relatively low average fee rates.

Therefore:

More transactions
≠
Automatically higher fees

Fees depend more directly on competition for block space and transaction characteristics than on the raw number of transactions alone.

Average input and output values also vary significantly between days.

However, a high average transaction value should not automatically be interpreted as greater economic activity because Bitcoin transactions may represent:

internal wallet movements
exchange transfers
UTXO consolidation
change outputs
wallet restructuring
9. Q06 - Largest Transactions

The sixth query searches for transactions with the largest total input values.

SELECT
  `hash` AS txid,
  block_timestamp,
  block_number,
  input_count,
  output_count,
  input_value,
  output_value,
  fee,
  virtual_size,
  SAFE_DIVIDE(fee, virtual_size) AS fee_rate_sat_vb
FROM `bigquery-public-data.crypto_bitcoin.transactions`
WHERE block_timestamp_month = DATE('2026-09-01')
  AND is_coinbase = FALSE
ORDER BY input_value DESC
LIMIT 20;
Observation

Transactions with total input values close to:

50,000 BTC

were observed.

One transaction contained approximately:

49,670 BTC

in total input value.

Inspection with mempool.space showed that this value came from several input UTXOs.

The transaction then created an output of approximately:

49,410 BTC

which was spent again only a few blocks later.

The transaction fee was only a few thousand satoshis.

This behavior strongly suggests that very large transaction values do not necessarily correspond to payments between two different users.

They may represent:

exchange wallet management
internal fund transfers
UTXO consolidation
wallet sweeps
cold-storage movements
address restructuring

Therefore:

High on-chain transaction value
≠
High economic payment

This is an important limitation when interpreting blockchain data.

The blockchain shows how coins move between scripts and addresses, but it does not directly reveal the real-world economic intent behind those movements.

10. BigQuery Query Cost

During experimentation, some queries required large scans.

Examples included queries processing:

~100 GB
~200 GB

More complex queries involving nested inputs and outputs could require several hundred gigabytes.

This illustrates an important BigQuery concept:

Query cost depends mainly on data scanned

and not on the number of rows returned.

For example:

LIMIT 20

does not mean BigQuery reads only 20 rows if it must first scan and sort millions of transactions.

Therefore, efficient BigQuery usage requires:

partition filtering
selecting only necessary columns
avoiding unnecessary nested fields
avoiding SELECT *
checking the estimated processed data before execution
11. From Individual Transactions to Large-Scale Analysis

Part 2 analyzed individual transactions using the Blockstream API.

Part 3 applies similar concepts to millions of transactions.

The progression can be summarized as:

Part 2

TXID
 ↓
API
 ↓
One transaction
 ↓
Python analysis

versus:

Part 3

Bitcoin public dataset
 ↓
SQL
 ↓
Millions of transactions
 ↓
Aggregation / filtering
 ↓
Statistical analysis

This demonstrates the difference between transaction-level investigation and large-scale blockchain analytics.

12. Main Lessons from Part 3

The main concepts learned are:

how to access Bitcoin public data using BigQuery
how to inspect a large blockchain dataset schema
how to query millions of Bitcoin transactions with SQL
how to use partition filters to reduce data scanning
how to calculate fee rates directly in SQL
how to calculate statistical distributions and quantiles
how to aggregate transaction activity by day
how to identify extreme transactions
how to inspect very large value transfers
why large on-chain values do not necessarily represent economic payments
why transaction interpretation requires contextual analysis
how BigQuery query cost depends on scanned data rather than returned rows
how to export query results to CSV for reproducibility
13. Part 3 Files

The work produced during this part is organized as:

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

Each result can therefore be traced directly to the SQL query that generated it.