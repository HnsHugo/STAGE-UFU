# Coinbase receipt support

The external FSF comparison history exposes coinbase inputs with `prevout: null`. The reconciled profile extractor previously attempted to access a dictionary method on this value and failed. It now handles null previous outputs and excludes coinbase inputs from sending-counterparty counts: coin creation has no sending address. Receipt amounts and receipt transaction counts still include these transactions; fees accrue only on address spends.

Two regression tests cover a coinbase receipt and its subsequent spend. All five Real-CATS unit tests, six theft-case tests and four collection tests pass. All ten previously saved external 19-feature profiles reproduce exactly after the correction. Model settings, feature names, training split and threshold remain unchanged.

This fixes an extraction edge case; it does not establish that all 19 feature conventions match the source dataset for mining-related histories. Donation purpose does not certify the provenance of every received payment.
