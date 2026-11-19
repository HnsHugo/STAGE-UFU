# BTCPay Server Bitcoin source pilot

The November 2026 BTCPay Server incident is the candidate for a later
held-out test of the pooled Coldcard and CryptoBilis classifier. The target is
membership in a documented source cohort. The [previous BTCPay diagnostic](../btcpay_transfer_protocol_20261022.json)
concerns the August 2026 Lightning case.

## Verified starting point

The BTCPay advisory names a reported Bitcoin destination and gives bounds on
its attribution. Bitquery traces 534 Bitcoin sweeps and estimates 18.38 BTC
across its scoped trace. Those totals are reported context for the pilot.
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/) ·
[Bitquery trace](https://www.bitquery.io/investigations/btcpay-server-hack)

| Check | Outcome |
| --- | --- |
| Published reference payment | `8e25f0…ec11`, 1 November 2026, block 974,152 |
| Destination | The sole output matches the Bitcoin address in the advisory |
| Explorer input counts | 566 inputs, 565 distinct addresses in one linked transaction group |
| Balance check | 185,813,170 sat in, 185,736,366 sat to the collector and 76,804 sat in fees |
| Individually visible records | 11 distinct addresses, including 5 indexed inputs with their previous outpoints |
| Exact matches with development | Zero of those 11 addresses and zero reference-payment matches among 1,500 Coldcard and 366 CryptoBilis selections |

The full TXID and source links are in the [protocol](protocol.json). The
[transaction record](https://btcintel.io/tx/8e25f0a572f562dd12514607eac4687408af09df8ccacd41e9acc66cea54ec11)
shows these witnesses across the address summary and input table. The [audit](audit.json)
retains their SHA-256 digests, the transaction arithmetic and the fingerprints
of the two development views. The individual overlap check covers the visible
11 addresses. The remaining reported inputs, cross-sweep links and merchant
ownership require further evidence.

## External test readiness

The first reference establishes one observed group. Counting the groups
available for evaluation requires a complete reference-input census across
additional sweeps, verification of funding links and an overlap audit with
development histories. Select contemporaneous comparison addresses after that
census. Each predictor must use the same fourteen definitions and confirmed
transactions strictly below its reference block. Record the support by
transaction group so one merchant sweep cannot obscure the results for smaller
groups. The pilot has zero selected comparisons, zero reconstructed feature
vectors and zero evaluations.
