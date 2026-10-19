# Coldcard case: verified flow findings

The roles below describe the observed transactions. The amounts are not an independent estimate of the stolen amount, and addresses prove neither identity nor control of a hardware wallet.

## Exercise address

`bc1qnk4zh9qcnap2mycp56qjrgza3cc8ylrh8fecp0`

Within the 98 supplied blocks, 504 transactions fund this address: **594.47725695 BTC** in total. The file alone provides partial coverage.

The confirmed history collected on 2026-10-14T23:02:05.172535+00:00 contains **507 transactions**, including **506 incoming** and **1 outgoing**. Pagination is complete and stable counters have been reconciled: **594.47728031 BTC received**, **562.02666941 BTC in consumed outputs**, observed balance **32.45061090 BTC**. This checks the provider's counters; it is not a cryptographic proof.

Incoming transactions have **505 distinct input addresses**; 0 input slots have no decoded address. This is not a victim count. 2 transactions in this history are absent from the supplied blocks.

Receipt confirmations range from 2026-07-30T01:36:08+00:00 to 2026-08-19T03:21:08+00:00 (1734300 seconds). This full activity span is not a demonstrated theft duration.

## Subset spent in the case consolidation

Transaction `0c6bf853a645b699a3b2cd6d8e3c44cf1a02a16f538df08212a44753f75d9d01` consumes **341 outputs** from **341 recovered parent transactions**. Their value is **562.02666941 BTC**. It creates one output of **562.01962301 BTC** and pays **704640 satoshis** in fees.

The recovered parents use **341 distinct input addresses**. The consolidation's own inputs are at the collection address; counting them as original source addresses would give a misleading result.

From the first recovered parent to the consolidation, the gap between the provider's transaction timestamps is **947 seconds**. Parent confirmation timestamps span 412 seconds. These are distinct measurements and do not establish the actual start of an incident.

## Other destinations in the case structure

The five source-attributed consolidations yield the following destinations. They remain graph leads; no guilt is inferred.

| Destination | Output BTC | Parents recovered / requested | Input addresses of recovered parents |
|---|---:|---:|---:|
| `bc1qq85v2c926eg6pgxhwp6q7lf6cnsz80qs3fcu9r` | 562.01962301 | 341 / 341 | 341 |
| `bc1qx76cae2706qd5q576feh7xq8rfcsjpf2htfhe3` | 398.47573857 | 491 / 491 | 491 |
| `bc1pdl33jtqnausmx2d4r4c6wpnk5are8jz046y3yjkw8fryjel02p7sluu9ce` | 36.01585057 | 34 / 101 | 34 |
| `bc1q8jy96fe5lf8vfugydnte3cguk92gpev7kwtp3q` | 89.62327890 | 204 / 204 | 204 |
| `bc1qtfrwa4j6rmj9rsgspv6a0yjumkg39js2numu75` | 45.90251994 | 0 / 1212 | 0 |

Sum of unique outputs from these cinq consolidations: **1132.03701099 BTC**. Do not add parent deposits to this sum: that would count the same funds again. Of 2349 distinct referenced parent transactions, 1070 are available. The missing transactions prevent a complete count of source addresses.

## Subsequent spending

5 of 5 outputs have a usable provider response; **0 are reported as spent**. The exact dates and URLs of each query appear in `case_flows.json`. An unspent output does not demonstrate cold or hardware storage. The collection-address balance and the status of these consolidation outputs are two different things.

## Scope and reproduction

Numerical results are computed from the data and accompanied by their SHA256 hashes in `case_flows.json`. No amount is converted to dollars without a date and exchange rate. No model is trained here.

```bash
python analyze_case_flows.py analyze /path/to/blocos.tgz new_output \
  --history /path/to/coldcard_target_history_20261014.json.gz \
  --outspends /path/to/coldcard_seed_outspends_20261014.json
```

Public observations may change. For a new collection (a new file is required):

```bash
python analyze_case_flows.py collect new_history.json.gz --max-pages 100
```

Attribution source: https://bitquery.io/investigations/coldcard-wallet-hack. Output verification does not confirm this source's allegations.
