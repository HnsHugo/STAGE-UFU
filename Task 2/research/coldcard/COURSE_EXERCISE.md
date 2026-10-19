# Exercise from Ivan's course material: 100 transactions + 100 comparisons

Primary source: `aula4.pdf`, Ivan Sendin, September 24, 2026, pages 97 and 99, provided by Hugo. The material specifies the address `bc1qnk4zh9qcnap2mycp56qjrgza3cc8ylrh8fecp0`, ten features and a decision tree. It then asks students to evaluate the classifier and search for other destinations. The code and results below complete this exercise without replacing the existing grouped experiments.

## Executed protocol

The 98 blocks contain 493,571 unique transactions, of which 504 pay the course address. The cohort contains 100 of these payments, selected by a deterministic SHA256 ranking of TXIDs with seed 42, and 100 unattributed transactions selected in the same way from the same blocks, with matching counts per block. Other candidate parents, the five attributed consolidations and coinbase transactions are excluded from the comparison group.

The features are `size`, `weight`, `fee`, sum/minimum/maximum/mean/standard deviation of values, and input and output counts. We interpret the values `v` as output values in satoshis; the material does not explicitly define `v`. The standard deviation is the population standard deviation (`ddof=0`). Address, TXID, block and label are not model variables.

The fixed stratified split retains 70 + 70 transactions for training and 30 + 30 for the descriptive test. The parameters chosen before execution are depth 4, a minimum of 5 rows per leaf and seed 42. These are implementation choices, not instructions from the course material. No tuning was performed based on the result.

## Result and explanation

| Descriptive test of 60 transactions | Count |
| --- | ---: |
| Payments to the address recovered | 30 / 30 |
| Comparison transactions not flagged | 30 / 30 |
| Errors observed in this sample | 0 |

The learned classification behavior reduces to **fees above 2,815 satoshis**. The lower-fee branch contains an additional split, but both of its leaves predict the comparison class. A total fee is not a fee rate; it also depends on transaction size. This separation describes the sample and does not characterize theft or a hardware device.

The sets share the same address and incident, and are matched on the same blocks. The artificial prevalence of 50% does not represent the blockchain. The 100% scores therefore do not constitute independent validation. The historical grouped validation remains more informative: it recovers 874/1,070 candidates, with 1,072 background alerts and mean recall across groups of 55.20%.

## Search for destinations to examine

The frozen tree from this exercise was applied to **492,135 unused unattributed transactions**. It flags **8,158**, whose outputs list **79,413 distinct addresses**. The report retains the twenty destinations appearing in the largest number of flagged transactions, together with at most three example TXIDs per destination.

This address count is partly due to transactions with many outputs. An alert concerns a transaction; it does not automatically identify all its outputs as malicious. Aggregated amounts are gross output flows, not balances or stolen amounts. None of the twenty destinations is promoted to a newly confirmed incident. The result answers the request to search for candidates, but above all demonstrates the need to independently verify each address's role.

A supplementary review on October 15 compares the twenty leads with the initial pilot's registry and searches for public sources for the top three. The second, `bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h`, was already a historical Binance reference. The official account's publication [Binance Blog, Our Commitment To Transparency](https://www.binance.com/en/square/post/51094) lists it in a wallet snapshot dated November 10, 2022. It does not establish its current owner, its individual hot/cold status or the origin of each payment. It is therefore not a newly discovered theft address. The other leads remain unresolved; uncorroborated search results were not converted into labels. The details and limitations of this bounded review are retained in `candidate_review_20261015.json`.

## Reproduction

From `Task 2/research/coldcard`, with a new output directory:

```bash
python course_baseline.py /path/to/blocos.tgz /path/to/parents.json new_output
python -m unittest discover -p 'test_course_baseline.py'
```

`course_results_20261014/` contains the 200-row cohort with its split, the readable tree, and the report with input hashes, parameters and limitations. The three tests check units and standard deviation, block matching independent of read order, and rejection of an insufficient comparison pool.
