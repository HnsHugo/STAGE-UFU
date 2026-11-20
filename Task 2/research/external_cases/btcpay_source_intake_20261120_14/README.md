# BTCPay Server source intake, batch 14

Both pending references from the collector page have complete public
transaction tables. The linked block pages confirm their heights and hashes
at [974,160](https://bitcoin.prod.gke.papers.tech/block/974160) and [974,158](https://bitcoin.prod.gke.papers.tech/block/974158).
Each transaction has a single output to the collector named in the
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).

| Payment | Block | Input rows | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [`e18a0c4fb397`](https://bitcoin.prod.gke.papers.tech/tx/e18a0c4fb3975eb7b0d4a856088a97305098d62de567c19bb000ffb4eb4601de) | 974,160 | 2 | 2,170,463 | 2,168,463 | 2,000 |
| [`f9010200b49d`](https://bitcoin.prod.gke.papers.tech/tx/f9010200b49d6ae965f28b99a840a5e5755a46cdec6e3b160e6ee49c793ffa16) | 974,158 | 1 | 11,562 | 11,200 | 362 |
| **Total** | | **3** | **2,182,025** | **2,179,663** | **2,362** |

The input values reconcile to the displayed totals and to collector output
plus fees. The [registry](source_registry.json.gz) adds three distinct
address fingerprints grouped by payment. There are zero exact address
matches between the groups or with earlier BTCPay observations. The pinned
Coldcard and CryptoBilis selections have zero exact address or reference-TXID
matches with this batch. Links between groups, merchant identity and
individual compromise remain unverified.

The cumulative registry covers **2,469 distinct addresses across 28 documented
payments**. Twenty-seven have reconciled input tables. The partial pilot
retains its 11 visible addresses. This batch adds zero complete individual
histories. Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part14.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `c5f4f711697ab789d2b2a176a8f942ec8bedfef7e43d574d2abda432f41435c7`.
The [protocol](protocol.json) pins the earlier registries, lists the documented
TXIDs and records two pending leads from the same collector page.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part14.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_14/protocol.json"
```
