"""Publish the verified/saved checkpoint's human-readable campaign state."""
import argparse
import textwrap
from pathlib import Path

from prepare_frontier_checkpoint import read, write

BASE = Path(__file__).resolve().parent
CAMPAIGN = BASE / 'mempool_fifty_20261112'


def report(out):
    out = out.resolve(); q = read(out / 'protocol.json'); a = read(out / 'coverage_audit.json')
    receipt = read(out / 'run_receipt.json'); backup = read(out / 'private_cache_backup.json')
    state = read(CAMPAIGN / 'progress.json'); resume = read(out / 'resume_checkpoint.json')
    assert backup['saved_privately'] and backup['library_metadata_applied'] and a['status'] == 'passed'
    state.update(status='checkpoint_saved' if state['pending_source_ids'] else 'all_fifty_saved', active_scope=None)
    for u in state['completed_units']:
        if u['scope'] == out.name:
            u.update(private_evidence_saved=True, private_evidence_sha256=backup['sha256'])
    write(CAMPAIGN / 'progress.json', state)
    table='\n'.join('| {source_id} | {status} | {saved_native_pages} |'.format(**d) for d in a['source_progress'])
    text=f'''# Verified durable checkpoint: {out.name}

The same frozen fifty-source campaign continues after temporary-workspace loss.
The earlier unarchived candidates were not promoted. This checkpoint reuses the
verified preceding view and frozen source/reference identities, preserving the
original incident-membership target, unknown theft/device labels and fourteen
predictors strictly before the reference block. No fit, score, split or threshold
change occurred. Full-current statuses and every older queue remain unchanged.

| Measure | Verified result |
|---|---:|
| Selected in this checkpoint | {a['selected']} |
| Finalized in this checkpoint | {a['finalized']} |
| Newly complete prefixes | {a['new_complete_prefixes']} |
| Bounded histories | {a['bounded_in_scope']} |
| Unfinished selected sources | {a['pending_in_scope']} |
| Fresh HTTP200 responses | {receipt['http200']} |
| Fresh request records | {receipt['provider_requests']} |
| Failed records | {receipt['failures']} |
| Preceding vectors preserved | {q['baseline_vectors']} |
| Coldcard vectors now available | {a['available_coldcard_vectors']} / 1,500 |
| CryptoBilis vectors, unchanged | 329 / 366 |
| Information gaps retained across both cohorts | {a['total_remaining_bounded_prefixes']} |
| Private evidence files verified and saved | {backup['private_files_verified']} |

| Frozen source ID | Outcome | Recorded native pages |
|---|---|---:|
{table}

Both audits pass: response/cursor fingerprints and raw assembly, original UTXO
extraction, separate feature recount and old-vector/identity/label/cutoff
invariants. Empty native terminal page, fresh reference anchors and funding
closure are mandatory for completeness. A bounded history keeps null features
and its actual private native cursor. Indexed coverage is not a cryptographic
inclusion proof or a full-current-history counter audit. Fresh observations are
source-transaction pairs, not globally unique coverage versus old Blockstream
prefixes. No unsupported hardware-wallet or theft label is inferred.

One worker, five-second spacing and a forty-five-second response timeout were
used with verified TLS and the inherited proxy. No provider/account/IP/proxy
rotation, paid service or in-scope request retry. The closed Blockstream gate
stays unchanged. The scope is closed, locks free, lease idle and automation
disabled. All private evidence is verified and saved.

Campaign total: {len(state['finalized_source_ids'])}/50 finalized,
{len(state['new_complete_source_ids'])} complete prefixes and
{len(state['bounded_source_ids'])} bounded histories; {len(state['pending_source_ids'])} pending.

{textwrap.fill(resume['next_action'],width=82)}
'''
    (out / 'RESULTS.md').write_text(text)
    p=out / 'README.md'
    p.write_text(p.read_text()+f'\nVerified result: [RESULTS.md](RESULTS.md). All private evidence is saved.\n')
    ledger='\n'.join(f"| {u['scope']} | {len(u['finalized_source_ids'])} | {len(u['new_complete_source_ids'])} | {u['http200']} |" for u in state['completed_units'])
    (CAMPAIGN / 'RESULTS.md').write_text(f'''# Fifty-source campaign: verified saved progress

The original source selection is unchanged. Smaller checkpoints follow the
temporary-workspace reset; lost unarchived candidates were not promoted.

{len(state['finalized_source_ids'])}/50 sources are finalized: {len(state['new_complete_source_ids'])}
complete prefixes, {len(state['bounded_source_ids'])} bounded histories and
{len(state['pending_source_ids'])} pending sources. Coldcard has
{state['available_coldcard_vectors']}/1,500 vectors; CryptoBilis remains 329/366.
Every old vector, unknown label, cutoff, full-current status and older queue is
preserved. No model fit or score. Each listed checkpoint is audited and saved.

| Scope | Finalized | Newly complete | HTTP200 |
|---|---:|---:|---:|
{ledger}
''')
    entry=f'''**Verified saved fifty-source checkpoint — 13 November 2026**

[The latest recovery checkpoint](research/coldcard/{out.name}/RESULTS.md)
finalized {a['finalized']}/{a['selected']} selected sources: {a['new_complete_prefixes']} newly complete prefixes,
{a['bounded_in_scope']} bounded histories and {a['pending_in_scope']} unfinished sources. It made
{receipt['provider_requests']} requests ({receipt['http200']} HTTP200; {receipt['failures']} failed records).
Both audits pass; all {q['baseline_vectors']} preceding vectors and protected identities,
unknown labels, cutoffs, full-current statuses and models/scores are unchanged.
All {backup['private_files_verified']} private evidence files are verified and saved. Coldcard now has
{a['available_coldcard_vectors']}/1,500 vectors; CryptoBilis stays 329/366.

The frozen campaign has {len(state['finalized_source_ids'])}/50 finalized: {len(state['new_complete_source_ids'])}
complete prefixes and {len(state['bounded_source_ids'])} bounded histories; {len(state['pending_source_ids'])} pending.
Lost unarchived candidates were not promoted. Continue only the remaining frozen
IDs in distinct five-source checkpoints, with audit/private save/publication
before each successor. Keep the forty-five-second timeout, one worker,
five-second spacing, live provider gate, fresh locks and exact published lease/
readback. Never restart a consumed scope or rotate provider/account/IP/proxy/TLS.
No paid service, fit, score or automatic schedule. Retain every actual native
cursor, missing row and deep history. Recheck overlap before model work.

The scope is closed, lease idle and locks free. This current checkpoint supersedes
older execution guidance while retaining the original fifty-ID selection.

'''
    for name in ['AGENTS.md','ALIGNMENT.md','PROJECT_STATUS.md']:
        p=BASE.parents[1]/name; s=p.read_text();h,t=s.split('\n',1);p.write_text(h+'\n\n'+entry+t.lstrip('\n'))
    return dict(finalized=len(state['finalized_source_ids']), complete=len(state['new_complete_source_ids']), pending=len(state['pending_source_ids']))


if __name__ == '__main__':
    import json
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('scope',type=Path);a=p.parse_args()
    print(json.dumps(report(a.scope),sort_keys=True))
