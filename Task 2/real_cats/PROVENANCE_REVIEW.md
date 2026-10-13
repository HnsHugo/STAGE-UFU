# Real-CATS provenance review before exploratory training

Primary methodological source: https://arxiv.org/html/2501.15553v1, Section 3.1 and feature table.
Pinned data source: https://github.com/sjdseu/Real-CATS/tree/054c659412a07d1dac596f625d02a84039f22a9b

The authors derive abuse categories from submitted reports. Benign addresses are selected as next-hop recipients of exchange hot-wallet withdrawals, relying on an assumption about exchanges' KYC practices. This is a comparison-selection policy, not address-by-address independent legitimacy verification. The downloaded revision's actual counts take precedence over aggregate counts from other paper/repository versions.

Exact-address searches for the pilot Hack and Theft references did not yield a separately verifiable incident-role source in this review. Both rows have watchback_checked=-1 and gs_checked=-1; these values are not used to manufacture confirmation or negative labels. Case IDs, historical label-availability dates and victim/recipient roles remain unresolved. Registry records remain pending review; they are not promoted to independently verified theft labels.

The feature table resolves Bitcoin monetary units: balance, total_received_BTC and total_sent_BTC are in satoshis despite their names. Lifetime is in seconds. Features still summarize full histories and are not substituted for the separate 24-hour cutoff-safe snapshots.

The authorized experiment therefore learns only original source categories: active Hack/Theft versus active benign. Other reported abuse categories and inactive rows are excluded. No BTCPay/FBI/Binance recipient is added as a training positive, and no victim is labeled criminal. This is an exploratory offline benchmark, not the independently sourced theft detector still required by the project.
