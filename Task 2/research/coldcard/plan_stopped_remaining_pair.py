"""Verify saved seeds for both pending targets without authorizing network traffic.

The consumed unit 20 stays closed. This is an offline readiness checkpoint;
it neither extends the original campaign selection nor opens its provider gate.
"""
from pathlib import Path
import hashlib
from prepare_frontier_checkpoint import read,sha,write
import recorded_remaining_campaign as campaign
from deferred_seeded_bridge import verify_seed
from planned_funding_bridge import legacy_source
from independent_mempool_bridge import choose_bridge
from independent_mempool_pilot import core

def prepare():
 b=campaign.BASE;state=read(campaign.CAMPAIGN/'progress.json')
 assert set(state['pending_source_ids'])=={'comparison_0026','comparison_0157'}
 assert state['active_scope']is None and state['can_continue']is False
 stopped=b/'mempool_remaining_fifty_20261116_unit_20';work=b/('source_cohort_work_'+stopped.name)
 q=read(stopped/'protocol.json');receipt=read(stopped/'run_receipt.json')
 assert receipt['status']=='stopped'and receipt['error']['error_type']=='SocketTimeoutError'
 assert receipt['provider_requests']==3 and receipt['http200']==2 and receipt['failures']==1
 assert read(stopped/'private_cache_backup.json')['saved_privately']
 assert read(stopped/'independent_verification.json')['status']=='passed'
 record=read(work/'plan.json')[0];assert record['pilot_id']=='comparison_0026'
 pins={m['key']:m for m in read(stopped/'legacy_reuse_manifest.json')['responses']}
 anchor,pages,values,_=legacy_source(record,work,pins);bridge,_=choose_bridge(record,anchor,values)
 seed=work/'requests'/'comparison_0026'/'boundary.json';marker=read(seed)
 assert marker['http_status']==200 and sha(seed.with_suffix('.json.gz'))==marker['sha256']
 assert marker['endpoint_sha256']==hashlib.sha256(('/tx/'+bridge['txid']).encode()).hexdigest()
 assert core(read(seed.with_suffix('.json.gz')))==core(bridge)
 failed=work/'requests'/'comparison_0026'/'native_tail_0000.json';failure=read(failed)
 assert failure['error_type']=='SocketTimeoutError'and not failed.with_suffix('.json.gz').exists()
 assert failure['endpoint_sha256']==hashlib.sha256(('/address/'+record['address']+'/txs/chain/'+bridge['txid']).encode()).hexdigest()
 deferred=verify_seed();assert len(deferred['cache'])==13
 policy=read(campaign.POLICY);gate=policy['provider_access_policies'][campaign.PROVIDER]
 assert gate['no_new_probe_authorized']and policy['collector_lease']['state']=='idle'
 out=campaign.CAMPAIGN/'stopped_pair_readiness.json'
 report=dict(status='offline_seeds_verified_network_paused',pending_source_ids=state['pending_source_ids'],
  original_selection_sha256=sha(campaign.CAMPAIGN/'selection.json'),original_target_set_unchanged=True,
  provider_requests=0,network_authorized=False,next_network_attempt_not_before=gate['next_network_attempt_not_before'],
  next_action='After the saved cooldown, use a distinct pinned successor for BOTH pending targets, fresh locks and exact published lease; preserve original stopped scopes.',
  targets=[dict(source_id='comparison_0026',origin_scope=stopped.name,legacy_pages=len(pages),
   cached_native_pages=0,cached_bridge_responses=1,failed_original_page_intents=1,maximum_new_page_intents=49,
   effective_native_replay_page_cap=49,original_failure_marker_sha256=sha(failed),original_bridge_marker_sha256=sha(seed)),
   dict(source_id='comparison_0157',origin_scope='mempool_remaining_fifty_20261116_unit_12',
   legacy_pages=deferred['legacy_pages'],cached_native_pages=12,cached_bridge_responses=13,
   unknown_original_page_intents=1,maximum_new_page_intents=37,effective_native_replay_page_cap=49,
   original_unknown_marker_sha256=deferred['original_unknown_marker_sha256'],original_unfinished_raw_sha256=deferred['original_unfinished_raw_sha256'])],
  collector_requirements=['Reuse every cached boundary/page; fresh reference checks and terminal funding closure retain their original budgets.',
   'A successor can replay 49 native pages for each row: 49 new for comparison_0026, 12 cached plus 37 new for comparison_0157.',
   'Keep cached tape records separate from live provider request receipts. Count each original failed/unknown intent against its own original 50-attempt cap.',
   'Do not call deferred_seeded_bridge.py prepare unchanged: its sole-pending-source precondition is no longer satisfied.',
   'Freeze an explicit two-target supplemental selection without modifying the original selection, and extend global verification for that exact selection.',
   'Do not reopen original unit 20, skip comparison_0026, weaken the strict crossed-boundary validator, or double-count replayed union observations.'],
  model_fits=0,new_scores=0,automation_enabled=False)
 write(out,report);return report

if __name__=='__main__':print(__import__('json').dumps(prepare(),indent=2))
