# BTCPay Server source intake, batch 10

The two pending references from the collector page were accessible for this
batch. Both are confirmed in [block 974,163](https://bitcoin.prod.gke.papers.tech/block/974163).
Their transaction pages agree with the linked block page on height and hash.
Each has a single output to the collector named in the
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).

| Payment | Block | Input rows | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [`9b95b28e6baf`](https://bitcoin.prod.gke.papers.tech/tx/9b95b28e6bafac28ec2ddfd8b9b00c40f22961fc57948f089054bb1cd59ff453) | 974,163 | 1 | 170,000 | 169,500 | 500 |
| [`fc4fba5c0459`](https://bitcoin.prod.gke.papers.tech/tx/fc4fba5c04593832bcee7be85a2ce9d71256daae5be79c2ac5bd4e9ef30d3241) | 974,163 | 1 | 59,292 | 58,692 | 600 |
| **Total** | | **2** | **229,292** | **228,192** | **1,100** |

Each input value reconciles to the displayed total and to the collector
output plus fee. The [registry](source_registry.json.gz) adds two distinct
input address hashes in two transaction groups. Exact address and
reference-TXID comparisons with the pinned Coldcard and CryptoBilis
selections found zero matches. Links between groups, merchant identity and
individual compromise remain unverified.

The cumulative registry covers **2,451 distinct addresses across 20 documented
payments**. Nineteen have reconciled input tables. The partial pilot retains
its 11 visible addresses. This batch adds zero complete individual histories.
Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part10.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `31ac8ff0a94889cc496121444b8cd0c2c729c5ff4418ac5fe7702ef933b9bb91`.
The [protocol](protocol.json) pins the earlier registries, lists all documented
TXIDs and records two pending leads from the same collector page.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part10.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_10/protocol.json"
```
