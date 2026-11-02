"""Audit and checkpoint a stopped bounded prefix successor without network IO."""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import gzip
import json
from pathlib import Path

from build_source_registry import digest, json_bytes
from source_cohort import atomic_write
import audit_reference_tail_successor as auditor
import collect_reference_tail as collector


def finalize(base, pass_name, reason):
    q=base/('source_'+pass_name+'_protocol.json')
    output=base/pass_name; work=base/('source_cohort_work_'+pass_name)
    policy_path=base/'comparison_access_retries_20261030/retry_policy.json'
    policy=json.loads(policy_path.read_bytes())
    parent_resume_path=base/policy['latest_prefix_resume_file']
    parent=json.loads(parent_resume_path.read_bytes())
    proto=json.loads(q.read_bytes())
    for p in proto['inputs'].values():
        if digest((base/p['file']).read_bytes())!=p['sha256']:
            raise ValueError('Pinned input changed')
    progress=collector.export(q,output,work)
    cp=json.loads(gzip.decompress((output/'checkpoint.json.gz').read_bytes()))
    entries=cp['entries']
    requests=json.loads(gzip.decompress((output/'request_manifest.json.gz').read_bytes()))
    stop_path=output/'collection_stop.json'
    if not stop_path.exists():
        atomic_write(stop_path,json_bytes(dict(stopped_at=datetime.now(timezone.utc).isoformat(),
            reason=reason,automatic_retry_performed=False,provider_or_route_changed=False)))
    baseline_pin=proto['inputs']['baseline_view']
    baseline=json.loads(gzip.decompress((base/baseline_pin['file']).read_bytes()))
    incomplete_requests=[m for m in requests if 'error_type' in m or 'sha256' not in m]
    if entries:
        summary=auditor.audit(q,output,work)
        view_path=output/'precutoff_feature_view.json.gz'
    else:
        view_path=base/baseline_pin['file']
        comparisons=[r for r in baseline['rows'] if not r['known_coldcard_core_membership']]
        summary=dict(schema_version=2,verified_at=datetime.now(timezone.utc).isoformat(),
            scope='Interrupted execution with no final source results; existing schema-v2 view reused unchanged.',
            targeted_sources=len(proto['source_ids']),targeted_results=0,targeted_pending=len(proto['source_ids']),
            targeted_statuses={},new_complete_pre_cutoff_comparisons=0,raw_tails_reextracted=0,
            independent_new_vectors_checked=0,saved_response_fingerprints_verified=0,
            case_predictors_available=sum(r['features'] is not None for r in baseline['rows'] if r['known_coldcard_core_membership']),
            comparison_predictors_available=sum(r['features'] is not None for r in comparisons),
            comparison_predictors_unavailable=sum(r['features'] is None for r in comparisons),
            complete_predictor_rows=sum(r['features'] is not None for r in baseline['rows']),
            full_history_comparison_statuses=dict(Counter(r['full_history_status'] for r in comparisons)),
            predecessor_predictor_vectors_preserved=sum(r['features'] is not None for r in baseline['rows']),
            all_predecessor_vectors_unchanged=True,labels_and_cutoff_unchanged=True,
            full_history_status_not_promoted=True,feature_count=14,training_performed=False,split_created=False,
            consumed_unfinished_requests_preserved=incomplete_requests,precutoff_view_sha256=digest(view_path.read_bytes()))
        atomic_write(output/'coverage_audit.json',json_bytes(summary))
        atomic_write(output/'coverage_summary.json',json_bytes(summary))
    complete=set(parent['excluded_complete_prefix_source_ids'])
    bounded=set(parent['excluded_bounded_incomplete_source_ids'])
    for key,e in entries.items():
        if key in complete or key in bounded:raise ValueError('Previously finished source repeated')
        if e['status']=='complete_prior_prefix':complete.add(key)
        elif e['status']=='bounded_incomplete':bounded.add(key)
        else:raise ValueError('Invalid final prefix status')
    pending=[key for key in parent['network_source_ids'] if key not in entries]
    denials=[m for m in requests if m.get('http_status') in (403,429) or 'Tunnel connection failed: 403' in m.get('reason','')]
    forbidden=any(m.get('http_status')==403 or 'Tunnel connection failed: 403' in m.get('reason','') for m in denials)
    rates=[m for m in denials if m.get('http_status')==429]
    if rates:
        local_delay=min(86400,max(7200,2*policy['last_retry_delay_seconds']))
        last=max(datetime.fromisoformat(m['finished_at']) for m in rates)
        due=last+timedelta(seconds=local_delay)
        for m in rates:
            ra=m.get('retry_after')
            if not ra:continue
            try:server=datetime.fromisoformat(m['finished_at'])+timedelta(seconds=float(ra))
            except ValueError:
                server=parsedate_to_datetime(ra)
                if server.tzinfo is None:server=server.replace(tzinfo=timezone.utc)
            due=max(due,server)
        policy.update(last_rate_limit_at=last.isoformat(),last_retry_delay_seconds=local_delay,
                      next_network_attempt_not_before=due.isoformat(),consecutive_429_stops_since_successful_access_check=1)
    def pin(path):return dict(file=path.relative_to(base).as_posix(),sha256=digest(path.read_bytes()))
    resume=dict(schema_version=2,updated_at=datetime.now(timezone.utc).isoformat(),
        scope=parent['scope'],bounds=parent['bounds'],network_source_ids=pending,network_sources=len(pending),
        excluded_complete_prefix_source_ids=sorted(complete),excluded_bounded_incomplete_source_ids=sorted(bounded),
        failed_consumed_requests=incomplete_requests,latest_work=work.name,
        full_history_comparison_statuses=summary['full_history_comparison_statuses'],
        prior_case_predictor_vectors=summary['case_predictors_available'],
        prior_comparison_predictor_vectors=summary['comparison_predictors_available'],
        next_network_attempt_not_before=policy['next_network_attempt_not_before'],
        resume_policy='Use only network_source_ids in a distinct pinned successor; preserve consumed markers in their stopped passes.',
        merge_policy='Preserve every predecessor vector, cutoff, label and full-history status in the latest schema-v2 view.',
        inputs=dict(protocol=pin(q),checkpoint=pin(output/'checkpoint.json.gz'),
            request_manifest=pin(output/'request_manifest.json.gz'),stop=pin(stop_path),
            feature_view=pin(view_path),audit=pin(output/'coverage_audit.json'),
            predecessor_resume=pin(parent_resume_path),validated_pilot=proto['inputs']['pilot_validation']))
    atomic_write(output/'resume_checkpoint.json',json_bytes(resume))
    status=('reference_tail_continuation_finished' if not pending else
            'reference_tail_continuation_stopped_403' if forbidden else
            'reference_tail_continuation_stopped_429' if rates else
            'reference_tail_continuation_interrupted_execution_control')
    policy.update(latest_prefix_output=pass_name,latest_output=pass_name,
        latest_prefix_protocol=q.name,latest_protocol=q.name,
        latest_prefix_work=work.name,latest_work=work.name,
        latest_prefix_result_file=pass_name+'/coverage_audit.json',latest_result_file=pass_name+'/coverage_audit.json',
        latest_prefix_resume_file=pass_name+'/resume_checkpoint.json',
        latest_prefix_stop_file=pass_name+'/collection_stop.json',latest_stop_file=pass_name+'/collection_stop.json',
        latest_status=status,automation_execution_status=status,latest_pass_pending_sources=len(pending),
        remaining_network_gap_sources=len(pending),prefix_network_pending_sources=len(pending),
        prefix_bounded_incomplete_sources=len(bounded),
        comparison_pre_cutoff_predictors_available=summary['comparison_predictors_available'],
        comparison_pre_cutoff_predictors_unavailable=summary['comparison_predictors_unavailable'],
        automation_confirmed_enabled=False,automation_environment_pause_reason=None,
        next_coverage_action=('Continuation network gaps resolved; retain bounded-incomplete prefixes and separate full-current-history coverage.' if not pending else
                             'Prepare a distinct successor over the latest network_source_ids, after lease/lock/cooldown checks; never rerun this stopped pass.'))
    policy['collector_lease'].update(state='idle',finished_at=datetime.now(timezone.utc).isoformat())
    if 'prepared_prefix_successor' in policy:policy['last_prepared_prefix_successor']=policy.pop('prepared_prefix_successor')
    policy['coverage_pause_reason']=('No continuation network gap remains.' if not pending else reason)
    atomic_write(policy_path,json_bytes(policy))
    return dict(status=status,summary=summary,network_remaining=len(pending),bounded_prefixes=len(bounded),resume_file=str(output/'resume_checkpoint.json'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pass_name');p.add_argument('reason')
    a=p.parse_args()
    print(json.dumps(finalize(Path(__file__).resolve().parent,a.pass_name,a.reason)))
