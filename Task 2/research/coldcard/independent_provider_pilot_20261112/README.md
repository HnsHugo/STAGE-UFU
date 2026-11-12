# Explicitly authorized independent-provider pilot

The user requests another acquisition method after HTTP429 on Blockstream.
The original 24-hour backoff is local policy, not a server Retry-After. Preserve
that stopped scope and its provider cooldown. This distinct pilot evaluates the
independent public Mempool API at its documented hostname, with a hard maximum
of 22 requests, one worker, five-second spacing and stop on first failure.
No proxy/IP/account/TLS change, paid service, automatic rotation or old-provider
request is part of this unit.

Reuse the 36 validated Blockstream reference/tail bodies for the first two
retained pending source/reference pairs. Compare the last cached transaction
against Mempool, independently check its continuation (including the saved
empty terminal page), and verify the reference block hash/height before and
after. Keep original UTXO funding closure and all fourteen prior-block features.
Record each provider's evidence separately. Unknown device/compromise labels,
full-current statuses, original cohort and old 1,401 complete vectors stay fixed.
No model or split. A provider or indexing disagreement prevents promotion.

The prototype remains subject to Mempool's own public limits. Higher-volume
options are separately authenticated service quotas or a self-hosted Bitcoin
Core/address indexer; neither is provisioned or purchased here. See
authorization_and_sources.json for the primary documentation.
