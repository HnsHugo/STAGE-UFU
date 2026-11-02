"""Prepare a distinct pinned successor after one saved successful counter check.

This preparation is offline. A stopped pass and its consumed markers stay intact.
Private plans, responses and caches remain in an excluded work directory.
"""
import argparse
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import re

from build_source_registry import digest, json_bytes
from source_cohort import atomic_write
import collect_reference_tail as tail


def prepare(base, pass_name, prior_plan, counter_result, counter_response):
    if not re.fullmatch(r'reference_tail_continuation_[0-9]{8}_[0-9]{4,6}', pass_name):
        raise ValueError('A unique dated continuation name is required')
    policy = json.loads((base/'comparison_access_retries_20261030/retry_policy.json').read_bytes())
    resume_path = base/policy['latest_prefix_resume_file']
    resume = json.loads(resume_path.read_bytes())
    now = datetime.now(timezone.utc)
    if datetime.fromisoformat(policy['next_network_attempt_not_before']) > now:
        raise ValueError('Saved cooldown is still active')
    counter = json.loads(counter_result.read_bytes())
    response = json.loads(counter_response.read_bytes())
    ids = resume['network_source_ids']
    if not ids or len(ids) > 100 or len(set(ids)) != len(ids):
        raise ValueError('Invalid bounded network-only selection')
    if counter.get('http_status') != 200 or counter['source_id'] != ids[0]:
        raise ValueError('A successful first remaining source counter check is required')
    if digest(counter_response.read_bytes()) != counter['response_sha256']:
        raise ValueError('Counter response fingerprint mismatch')
    if datetime.fromisoformat(counter['started_at']) < datetime.fromisoformat(policy['next_network_attempt_not_before']):
        raise ValueError('Counter check preceded the saved cooldown')
    excluded = set(resume['excluded_complete_prefix_source_ids'] + resume['excluded_bounded_incomplete_source_ids'])
    if set(ids) & excluded:
        raise ValueError('A finished prefix was selected again')
    all_records = json.loads(prior_plan.read_bytes())
    by_id = {r['pilot_id']: r for r in all_records}
    records = [by_id[key] for key in ids]
    if response.get('address') != records[0]['address'] or digest(records[0]['address'].encode()) != counter['address_sha256']:
        raise ValueError('Counter/source identity mismatch')
    inputs = {}
    visited = set()

    def pin(path):
        path = Path(path)
        relative = path.relative_to(base).as_posix()
        raw = path.read_bytes()
        if relative in visited:
            return
        visited.add(relative)
        inputs['lineage_%03d' % len(inputs)] = dict(file=relative, sha256=digest(raw))
        if path.suffix == '.json':
            data = json.loads(raw)
            for value in data.get('inputs', {}).values():
                if isinstance(value, dict) and 'file' in value and 'sha256' in value:
                    child = base/value['file']
                    if digest(child.read_bytes()) != value['sha256']:
                        raise ValueError('Historical pin changed: '+value['file'])
                    pin(child)

    pin(resume_path)
    for name, value in resume['inputs'].items():
        inputs['parent_'+name] = value.copy()
    inputs['baseline_view'] = resume['inputs']['feature_view'].copy()
    inputs['pilot_validation'] = resume['inputs']['validated_pilot'].copy()
    for name, file in dict(collector='collect_reference_tail.py', batch_runner='collect_reference_tail_many.py',
                          continuation_auditor='audit_reference_tail_successor.py',
                          feature_extractor='prepayment_pilot.py', transport='comparison_http.py',
                          ledger='collect_comparison_coverage.py').items():
        inputs[name] = dict(file=file, sha256=digest((base/file).read_bytes()))
    baseline = json.loads(gzip.decompress((base/inputs['baseline_view']['file']).read_bytes()))
    rows = {r['source_id']:r for r in baseline['rows']}
    for r in records:
        old = rows[r['pilot_id']]
        if old['features'] is not None or old['precutoff_history_status'] != 'not_completed':
            raise ValueError('Selected schema-v2 row already has a final result')
        for field in ('address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash'):
            if r[field] != old[field]:
                raise ValueError('Frozen source identity differs from baseline')
    work = base/('source_cohort_work_'+pass_name)
    output = base/pass_name
    q = base/('source_'+pass_name+'_protocol.json')
    if work.exists() or output.exists() or q.exists():
        raise FileExistsError('Never restart or overwrite a prepared pass')
    work.mkdir(); (work/'requests').mkdir(); (work/'raw').mkdir(); (work/'results').mkdir()
    atomic_write(work/'plan.json', json_bytes(records))
    requests = json.loads(gzip.decompress((base/resume['inputs']['request_manifest']['file']).read_bytes()))
    prior_work = base/resume['latest_work']
    reused = 0
    for r in records:
        metas = {m['key']:m for m in requests if m['source_id']==r['pilot_id'] and m.get('http_status')==200 and 'sha256' in m}
        cursor = r['payment_txid']
        for key in ['reference']+['tail_%04d'%i for i in range(16)]:
            meta = metas.get(key)
            body = prior_work/'requests'/r['pilot_id']/(key+'.json.gz')
            if meta is None or not body.exists():
                break
            raw = body.read_bytes()
            endpoint = '/tx/'+r['payment_txid'] if key=='reference' else '/address/'+r['address']+'/txs/chain/'+cursor
            if digest(raw) != meta['sha256'] or digest(endpoint.encode()) != meta['endpoint_sha256']:
                raise ValueError('Cached fingerprint or cursor endpoint differs')
            data = json.loads(gzip.decompress(raw))
            if key=='reference':
                tail.anchor_check(r,data)
            elif data:
                cursor=data[-1]['txid']
            folder=work/'requests'/r['pilot_id']; folder.mkdir(exist_ok=True)
            atomic_write(folder/(key+'.json.gz'),raw)
            atomic_write(folder/(key+'.json'),json_bytes(dict(meta,reused_from_predecessor=resume['latest_work'])))
            reused+=1
            if key!='reference' and not data:break
    proto=dict(schema_version=1,pass_name=pass_name,created_at=now.isoformat(),
        authorization='User-authorized continuation after the saved cooldown and one original-route counter HTTP200.',
        provider='https://blockstream.info/api',source_ids=ids,inputs=inputs,
        private_plan_sha256=digest(json_bytes(records)),batch_size=20,max_batches=5,
        workers=2,requests_per_second=1,max_pages_per_address=16,timeout_seconds=15,
        coverage_scope='Exhausted confirmed prefix strictly below the unchanged frozen cutoff; never full-current-history promotion.',
        labels='Unknown labels and all fourteen definitions are unchanged.',
        failure_policy='Stop new starts on first 403/429 or other failure; no internal retry or provider/route/account/proxy/IP/TLS change.',
        merge_policy='Compose with the latest pinned schema-v2 baseline and preserve every previous vector and full-history status.',
        normal_counter_access_check=dict(counter,repeat_inside_successor=False),
        predecessor_failed_markers_reused=False,
        successor_attempts_for_predecessor_denied_pages=resume['failed_consumed_requests'],
        denied_page_attempt_policy='Any new attempt occurs only in this distinct successor after cooldown; old consumed markers stay in their original passes.',
        predecessor_successful_responses_for_selected_sources=sum(m['source_id'] in ids and m.get('http_status')==200 for m in requests),
        verified_predecessor_responses_reused=reused,
        unavailable_private_response_policy='Absent predecessor private bytes cannot be reused; their published metadata is preserved. New requests for unfinished sources are recorded only in the successor.',
        predecessor_predictor_vectors=sum(r['features'] is not None for r in baseline['rows']))
    atomic_write(q,json_bytes(proto))
    output.mkdir()
    return dict(protocol=str(q),work=str(work),output=str(output),protocol_sha256=digest(q.read_bytes()),
                source_count=len(ids),pinned_inputs=len(inputs),reused_successful_responses=reused)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pass_name');p.add_argument('prior_plan',type=Path)
    p.add_argument('counter_result',type=Path);p.add_argument('counter_response',type=Path)
    a=p.parse_args()
    print(json.dumps(prepare(Path(__file__).resolve().parent,a.pass_name,a.prior_plan,a.counter_result,a.counter_response)))
