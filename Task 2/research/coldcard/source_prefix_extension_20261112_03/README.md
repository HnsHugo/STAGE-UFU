# Fixed frontier recovery and extension: twenty source/reference pairs

**Interrupted; retained evidence independently verified.** See [RESULTS.md](RESULTS.md).

The approved protocol, frozen source order, explicit old-body recovery
fingerprints and private evidence layer are preserved. Original refusals
and prelaunch review history remain immutable. No fit or score.

The live protocol forbids provider requests and early access probes before
**2026-11-13T18:22:14+00:00** (13 November, **15:22:14 America/Sao_Paulo**).
This is a lower bound under the existing progressive 24-hour backoff, not a
scheduled restart. No server Retry-After header was supplied. Both 429 requests
were already engaged before the first refusal; no new request intent followed it.
The clock-only CLI check returned COOLDOWN_NOT_DUE_NO_HTTP and created no work,
permit or request marker. Six further offline refusal/cooldown checks pass.

The stopped scope cannot be restarted. Its twenty original IDs stay pending;
eighteen were never started. Two sources retain seventeen pages each. One of
these has a saved empty terminal page but its required fresh reference-status
request was refused, so it is not promoted. See resume_inventory.json for all
36 reusable reference/tail fingerprints and a conservative 669-request bound
for a distinct successor through the same 32-page checkpoint.

A successor must pin its reuse manifest and use a resume-compatible guarded
runner/finalizer: the immutable fresh-recovery runner rejects offline flags, and
the untouched-frontier preparer must not skip these pending sources. Preserve
the empty terminal page; do not copy either consumed failed marker, the old
counter or any old reference-status marker. Keep the original route, fresh
historical/local locks and exact live lease publication/readback after cooldown.
The 42 untouched IDs, the earlier eighteen 32-page histories, three 576-page
cursors, all other missing rows and all 1,401 complete vectors remain retained.
