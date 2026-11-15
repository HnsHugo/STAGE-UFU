"""Create a distinct successor of the verified, no-network blocked unit."""
from contextlib import ExitStack
from pathlib import Path
import fcntl
import hashlib
import os
import shutil
from prepare_frontier_checkpoint import read, write, sha
from independent_mempool_resume import cached_prefix

B = Path(__file__).resolve().parent
C = B / 'mempool_native_round3_20261114'
OLD = B / 'mempool_native_round3_20261114_unit_02_recovery_20261115'
SCOPE = 'mempool_native_round3_20261115_unit_02_authorized'


def prepare():
    out, work = B / SCOPE, B / ('source_cohort_work_' + SCOPE)
    prior = B / ('source_cohort_work_' + OLD.name)
    assert not out.exists() and not work.exists()
    policy = read(B / 'comparison_access_retries_20261030/retry_policy.json')
    assert policy['collector_lease']['state'] == 'idle' and policy['active_collection_scope'] == 'none'
    stop = read(OLD / 'collection_stop.json')
    assert stop['new_provider_requests'] == 0 and stop['operational_locks_released']
    assert not (prior / 'lease_published').exists()
    q = read(OLD / 'protocol.json')
    for pin in q['inputs'].values():
        assert sha((OLD / pin['file']).resolve()) == pin['sha256']
    locks = set(read(prior / 'historical_locks.json')) | {str(prior / 'collector.lock')}
    locks.update(str(p / 'collector.lock') for p in B.glob('source_cohort_work_*'))
    with ExitStack() as stack:
        for name in sorted(locks):
            Path(name).parent.mkdir(parents=True, exist_ok=True)
            f = stack.enter_context(Path(name).open('a+'))
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        records = read(prior / 'plan.json')
        pins = read(OLD / 'offline_reuse_manifest.json')['responses']
        markers = [read(p) for p in (prior / 'requests').glob('*/*.json')]
        assert len(markers) == len(pins) == 405 and all(m.get('offline_reused') for m in markers)
        assert not list((prior / 'results').glob('*'))
        for r in records:
            _, pages, cursor, _, _, terminal = cached_prefix(r, prior, [m for m in pins if m['source_id'] == r['pilot_id']])
            assert len(pages) == 80 and not terminal
            assert hashlib.sha256(cursor.encode()).hexdigest() == hashlib.sha256(read(prior / 'parent_native_cursors.json')[r['pilot_id']]['cursor'].encode()).hexdigest()
        out.mkdir(); work.mkdir(mode=0o700)
        for name in ['requests', 'raw', 'results']:
            (work / name).mkdir()
        shutil.copytree(prior / 'requests', work / 'requests', dirs_exist_ok=True)
        for name in ['plan.json', 'remaining_source_registry.json', 'retained_bridge_native_cursors.json', 'parent_native_cursors.json']:
            shutil.copyfile(prior / name, work / name)
        write(work / 'historical_locks.json', sorted(locks))
        for name in ['offline_reuse_manifest.json', 'seed_manifest.json', 'retained_deep_queue.json']:
            shutil.copyfile(OLD / name, out / name)
        state = read(C / 'progress.json')
        assert state['next_unit'] == 2 and set(q['source_ids']) <= set(state['pending_source_ids'])
        state.update(status='prepared_unit', active_scope=SCOPE, can_continue=True)
        state.pop('blocker', None); state.pop('blocked_scope', None)
        write(C / 'progress.json', state); write(out / 'prepared_campaign_state.json', state)
        authorization = dict(authorized_on='2026-11-15', exact_user_message='continue je te donnes tous les acces',
            context='User replied to explicit request for publishing code/redacted reports to HnsHugo/STAGE-UFU branch task-2-wallet-analysis and continuing Mempool collection.',
            allowed_publication='Code and redacted reports only; private raw caches remain excluded.',
            allowed_provider='https://mempool.space/api', purpose='Existing frozen source/reference historical-prefix research; public Bitcoin address/transaction identifiers only.',
            bounds='One worker, five-second spacing, 45-second timeout, up to sixteen additional native pages per source; stop at first failure. No paid service or route/TLS change.')
        write(out / 'explicit_user_authorization.json', authorization)
        inputs = {k: (OLD / v['file']).resolve() for k, v in q['inputs'].items()}
        for k, p in list(inputs.items()):
            if p.parent == OLD:
                inputs[k] = out / p.name
        inputs.update(explicit_user_authorization=out / 'explicit_user_authorization.json',
            closed_predecessor=OLD / 'collection_stop.json', predecessor_readiness=OLD / 'offline_readiness_audit.json',
            authorized_successor_preparer=Path(__file__).resolve())
        q.update(pass_name=SCOPE, created_on='2026-11-15',
            authorization='Explicit user approval on 15 November: continue je te donnes tous les acces, in reply to exact GitHub publication and Mempool continuation question.',
            closed_blocked_predecessor=OLD.name)
        q['private_lock_manifest_sha256'] = sha(work / 'historical_locks.json')
        q['inputs'] = {k: dict(file=os.path.relpath(p, out), sha256=sha(p)) for k, p in inputs.items()}
        write(out / 'protocol.json', q)
        write(out / 'preparation_verification.json', dict(status='passed', old_pages_verified=400,
            cached_responses_verified=405, baseline_vectors=1439, input_pins_verified=len(inputs), provider_requests=0,
            all_historical_locks_verified_free=True, exact_user_authorization_recorded=True))
        (out / 'README.md').write_text('# Explicitly authorized distinct successor\n\nSame five frozen source/reference pairs and 400 verified native pages. Add at most sixteen pages per source. Target: operational core membership; theft/device status remains unknown. Fourteen predictors strictly precede the reference block. Baseline: 1,439 complete vectors. One worker, five-second spacing, 45-second timeout, same Mempool provider/route and verified TLS. Fresh locks plus exact published lease/readback are required. Audit, privately save and publish before a successor. Stop at the first failure; no retry, rotation, cost, fitting or scoring. Both closed predecessor scopes and unknown original outcomes remain preserved.\n')
    print(SCOPE + ': 405 saved responses verified; no new HTTP')


if __name__ == '__main__':
    prepare()
