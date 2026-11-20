# BTCPay Server source intake, batch 9

Two indexed public transaction tables from Trezor Bitcoin Explorer supplied the
evidence for this batch. The larger table was read in overlapping sections.
The sections agree where they overlap and cover every line through the
transaction footer. For both payments, the transaction and linked block pages
agree on the height and hash. Each has one output to the collector named in the
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).

| Payment | Block | Input rows | Distinct addresses | Inputs (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [`e8db837dc326`](https://bitcoin.prod.gke.papers.tech/tx/e8db837dc326270d32971464d8d7b1e26a1a3bc5880fb45e07823db626e47c34) | 974,189 | 420 | 410 | 49,353,309 | 49,296,082 | 57,227 |
| [`56aa0f058355`](https://bitcoin.prod.gke.papers.tech/tx/56aa0f0583552dd8978e39bc4adae8ac06cd57a89fc7f62563f11636110f7ab2) | 974,158 | 57 | 56 | 9,274,269 | 9,224,269 | 50,000 |
| **Total** | | **477** | **466** | **58,627,578** | **58,520,351** | **107,227** |

The rows reconcile to the listed input totals and to collector output plus
fees. The [registry](source_registry.json.gz) adds 466 distinct address
fingerprints across two observed co-input groups. There are zero exact
address matches between the two groups or with earlier observations. Exact
address and reference-TXID comparisons with the pinned Coldcard and
CryptoBilis selections also found zero matches. Links between groups,
merchant identity and individual compromise remain unverified.

The cumulative registry covers **2,449 distinct addresses across 18 documented
payments**. Seventeen have reconciled input tables, and the partial pilot
retains its 11 visible addresses. This batch adds zero complete individual
histories. Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part9.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `ee0c589211d0e17797a9a088a480c4751fa661cc357d502fa397b8cc87c8d406`.
The [protocol](protocol.json) lists all documented TXIDs and pins prior
registries. The two previously recorded page 33 candidates remain pending
because their public transaction tables were unavailable during screening.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part9.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_09/protocol.json"
```
