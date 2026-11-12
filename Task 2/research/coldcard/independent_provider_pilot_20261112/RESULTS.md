# Independent provider is reachable; naive cursor splice rejected

Mempool returned HTTP200 for all three requests. The frozen reference status
and the immutable boundary transaction core agree with the saved Blockstream
evidence. The first continuation page includes three already saved transactions
in the same boundary block, with identical immutable fields. The two indexes
have a different ordering inside that block. The strict duplicate check stopped
the pilot before any vector was promoted.

All 1,401 old vectors and every unselected row remain unchanged. Saved-response
checks and the independent row audit pass; all 81 private evidence files are
verified and saved. No Blockstream request, account, IP/proxy/TLS change, paid
service, fit or new score occurred. The original cooldown stays unchanged.

A distinct corrected pilot rewinds above the partially cached block, follows
Mempool-native cursors, verifies each overlap's immutable core, rejects unknown
transactions in previously complete newer blocks, and merges only by TXID.
This preserves completeness across differing intra-block orderings rather than
ignoring duplicates or weakening the original stopped scope.
