# Emergency backup priority — execution environment unavailable

The user explicitly prioritizes saving every unsaved result before continuing. The executor became unavailable during unit 17. Both command execution and host file upload failed because no primary execution environment is available.

## Confirmed durable checkpoint

All code is published. The latest independently verified, privately saved data checkpoint is unit 16, data commit [1a1aca0961b4a10aaef218b8f8fd12d6a94c5746](https://github.com/HnsHugo/STAGE-UFU/commit/1a1aca0961b4a10aaef218b8f8fd12d6a94c5746): 39/50 original histories processed, 7 newly complete, 1,457/1,500 complete vectors. Eleven pass targets and 43 full feature rows remain incomplete. There are 1,962 known successful responses, zero known failed provider intents and two explicitly unresolved historical intents. All 17,121 private evidence files counted at that checkpoint are saved. These counts exclude unsaved unit-17 traffic.

## Unsaved unit 17: last observation, not a recovered checkpoint

The last actual observation was **149 successful responses**, zero known failures, with `comparison_0391` and `comparison_0433` finalized as bounded histories and `comparison_0522` still collecting. More responses or a final receipt may exist; the outcome after that observation is unknown. Do not claim unit 17 has been backed up or independently audited, do not count its two finalized histories in the durable total, and do not invent the final request count or cursor.

Worktree: `/workspace/scratch/fc897d43bfda/STAGE-UFU`.
Working evidence: `Task 2/research/coldcard/source_cohort_work_mempool_remaining_fifty_20261116_unit_17/`.
Important subpaths: `requests/`, `raw/`, `results/`, `plan.json`, `remaining_source_registry.json`, `historical_locks.json`, and any `native_cursors.json`. The public unit directory may also contain locally generated checkpoint/manifest/progress files not yet pushed. Preserve the whole working tree before cleanup or replacement.

A direct backup attempt prepared three upload sessions but could not transfer bytes. No upload was finalized. Those preparations are **not backups**. A separate direct host-file upload also failed with `no primary turn environment is available`.

## Requested provider pause; local termination is unconfirmed

The repository policy is changed to `pause_requested`, retaining its original owner and `operational_locks_released=false`. **This is a published pause request only: the collector reads its local policy file, and delivery of the changed repository policy to that file is unconfirmed.** Publishing the remote policy does not prove that a running collector received the request. It may have continued, stopped or finished while access was lost. Once access returns, apply/confirm the pause locally before any new collection and inspect actual locks and outputs. No local stop, lock release, exact final count, or absence of an active collector has been verified. Do not publish an idle lease merely because the executor is inaccessible. The original lease is retained in `environment_recovery_snapshot.json`.

The campaign progress file remains the original prepared state so its pinned bytes are preserved. This emergency pause overrides its old `can_continue` value. Existing GitHub/Mempool permissions persist; no renewed permission question is needed.

## Recovery order

1. Regain execution/file access and inspect the existing worktree before cloning over or removing anything. Read the actual local receipt, all request markers/bodies, native cursor evidence and every relevant lock. The former exec session may no longer exist.
2. Save **every newly successful byte**, including unit-17 pages, statuses, finalized raw/results, partial third-source pages, metadata and any unknown intents. Copy and fingerprint evidence before administrative changes; privately archive it. A file that could not be read or transferred is not a confirmed backup.
3. Reconstruct and audit the exact result. If the original scope completed, verify and close it from the actual receipt. Otherwise close its real interrupted state, preserve original unknown outcomes and use a distinct pinned successor with actual saved cursors and remaining per-source page budgets. Never restart a consumed scope or request already saved pages again.
4. Publish the verified checkpoint, update the persistent resume note `STAGE_UFU_reprise_20261114.md`, then continue the remaining original targets. Only release the emergency pause after actual locks/outcomes and private backup are reconciled. An environment interruption or lease-guard stop is not a provider refusal.

The deferred original `comparison_0157` remains required. Its twelve saved native pages and original unknown intent are preserved in unit 12. After the ordinary units are saved, `deferred_seeded_bridge.py` supplies the separately frozen final unit using cached responses and at most 37 new page requests; use its special `run` and `finish` commands. The existing crossed-boundary validator is unchanged.

Preserve all original labels, cutoffs, complete vectors and queues. No model fit, score, paid service, provider/route/TLS rotation or background schedule. Bitcoin transaction relations are not proof of theft or hardware-wallet use.
