# BTCPay Server source intake, batch 5

The [payment at block 974,152](https://bitcoin.prod.gke.papers.tech/tx/b198d4f6263de98d6a4078df4eff9962639dd8dd2b037682386b2a3ed91a26fd)
has one output, to the collector named in the
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).
Its block height and hash agree with the [linked block header](https://bitcoin.prod.gke.papers.tech/block/974152).
The overlapping views of the explorer table cover every line through the
transaction footer.

| Input rows | Distinct input addresses | Input total (sat) | Collector output (sat) | Fee (sat) |
| ---: | ---: | ---: | ---: | ---: |
| 566 | 564 | 173,897,610 | 173,820,808 | 76,802 |

The input values sum to the displayed total and to collector output plus fees.
The [registry](source_registry.json.gz) retains all 564 distinct address hashes
in one observed co-input group. All 564 hashes are new to the registry.
The pinned Coldcard and CryptoBilis selections have zero exact address or
reference-TXID matches with this batch. Links between groups, merchant identity
and individual compromise remain unverified.

The cumulative registry covers **1,959 distinct addresses across ten
documented payments**, including 11 visible addresses from the partial pilot.
Nine payments have reconciled input tables. This batch adds zero complete
individual histories. Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part5.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `24a6ddb855392e912c049f52a1503c403d7e8e73af404a77f3c9717f6fbcb39e`.
The [protocol](protocol.json) lists all ten documented TXIDs, pins the earlier
registries and records two leads from the preceding collector page. Each lead
requires its own confirmed block and single-output check.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part5.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_05/protocol.json"
```
