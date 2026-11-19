# BTCPay Server source intake, batch 4

The two confirmed payments below each have one output, to the collector named
in the [BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).
The transaction views and the [linked block header](https://bitcoin.prod.gke.papers.tech/block/974153)
agree on the height and block hash. Both complete displayed input tables
reconcile to the input totals and to collector output plus fee.

| Payment TXID | Block | Input rows | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [`20f6c265a6dd`](https://bitcoin.prod.gke.papers.tech/tx/20f6c265a6dda063c6d3a4661610e2105f218a00e5b8fec810bf001602456306) | 974,153 | 2 | 50,765 | 50,165 | 600 |
| [`5d7e04554feb`](https://bitcoin.prod.gke.papers.tech/tx/5d7e04554feb294b967d8415e1d01a3a0b07be8b5ed86da538138867acfa01d9) | 974,153 | 5 | 759,600 | 753,600 | 6,000 |
| **Total** | | **7** | **810,365** | **803,765** | **6,600** |

The [registry](source_registry.json.gz) records seven distinct input-address
hashes. All seven are new to the BTCPay registry. Exact address and reference
TXID comparisons with the pinned Coldcard and CryptoBilis selections found zero
matches. Each payment defines its own observed co-input group. Merchant
identity, individual compromise and links between groups remain unverified.

The cumulative registry now covers **1,395 distinct addresses across nine
documented payments**. Eight payments have reconciled displayed input tables.
The [partial pilot](../btcpay_hot_wallet_pilot_20261119/README.md)
retains its 11 individually visible witnesses. This batch adds zero complete
individual histories. Future histories use strictly lower block heights than
their reference payment.

The candidate [`45ebfeab502f`](https://bitcoin.prod.gke.papers.tech/tx/45ebfeab502f4acce21c3bdb0aac1cb2549c555da06aa4fb780b04f52e123260)
has a second output of 11,562 sat and fails the
single-output condition. Its screening result and a pending reference from the
collector page are recorded in the [protocol](protocol.json), alongside all
documented reference TXIDs.

## Checkpoint and replay

The private evidence archive `BTCPay-source-evidence-20261120-part4.json.gz` was reopened and
matched byte for byte. Its SHA-256 digest is
`d5ed5eaf63df273f104ff5ff8848b74b754224aabc073d5ef6aa6c283784d79a`.
The published Coldcard lease remains marked running. This collection used
archived public views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part4.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_04/protocol.json"
```
