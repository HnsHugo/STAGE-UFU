"""Verify the fifty-row campaign while retaining interrupted evidence separately.

The original full-scope clock audits remain incomplete for units 12 and 13.
Their known successful responses and every unknown intent are counted explicitly.
"""
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path

from prepare_frontier_checkpoint import read, sha, write
import recorded_remaining_campaign as campaign
from recorded_mempool_resume import verify_dispatch_evidence
from recover_interrupted_remaining_unit import verify_interrupted_clock
from recover_native_unit13 import clocks


def verify():
    spec = importlib.util.spec_from_file_location('original_progress_verifier', campaign.CAMPAIGN / 'verify_progress.py')
    original = importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
    def dispatch(markers):
        if any((m['source_id'], m['key']) == ('comparison_0157', 'native_tail_0012')
                and 'finished_at' not in m for m in markers):
            return verify_interrupted_clock(markers)
        return verify_dispatch_evidence(markers)
    original.verify_dispatch_evidence = dispatch
    with redirect_stdout(io.StringIO()):
        report = original.verify()
    fragments = read(campaign.CAMPAIGN / 'progress.json').get('interrupted_evidence_fragments', [])
    extra_success = extra_pages = extra_observations = extra_files = 0
    evidence = []
    for fragment in fragments:
        out = campaign.BASE / fragment['scope']
        work = campaign.BASE / ('source_cohort_work_' + fragment['scope'])
        backup = read(out / 'private_cache_backup.json')
        assert backup['saved_privately'] and backup['library_metadata_applied']
        proof = read(out / 'interruption_recovery.json')
        assert proof['original_protocol_sha256'] == sha(out / 'protocol.json')
        for item in proof['original_request_markers']:
            assert sha(work / item['file']) == item['sha256']
        markers = [read(p) for p in sorted(work.glob('requests/*/*.json'))]
        assert clocks(markers) == read(out / 'dispatch_verification.json')
        for marker in markers:
            body = work / 'requests' / marker['source_id'] / (marker['key'] + '.json.gz')
            if marker.get('http_status') == 200: assert sha(body) == marker['sha256']
            else: assert not body.exists()
        audit = read(out / 'independent_verification.json')
        assert audit['status'] == 'passed' and audit['original_full_clock_audit'] == 'incomplete_unknown_intent'
        successor = campaign.BASE / fragment['recovery_scope']
        q = read(successor / 'protocol.json')
        assert q['inputs']['interruption_recovery']['sha256'] == sha(out / 'interruption_recovery.json')
        fresh = [m for m in read(successor / 'request_manifest.json.gz') if not m.get('offline_reused')]
        for sid, cap in q['per_source_new_page_caps'].items():
            old_endpoints = {m['endpoint_sha256'] for m in markers if m['source_id'] == sid
                and m['key'].startswith('tail_') and m.get('http_status') == 200}
            tails = [m for m in fresh if m['source_id'] == sid and m['key'].startswith('tail_')]
            assert len(tails) <= cap
            assert not old_endpoints.intersection(m['endpoint_sha256'] for m in tails)
            assert len(tails) + q['original_successful_new_pages'][sid] + q['original_unknown_page_intents'][sid] <= 50
        extra_success += proof['http200']
        extra_pages += fragment['new_native_pages']
        extra_observations += audit['fresh_native_source_transaction_observations']
        extra_files += backup['private_files_verified']
        evidence.append(dict(scope=fragment['scope'], http200=proof['http200'],
            successful_new_native_pages=fragment['new_native_pages'], unresolved_intents=1,
            original_full_clock_audit='incomplete_unknown_intent', original_markers_preserved=True))
    report.update(http200=report['http200'] + extra_success,
        successful_new_native_pages=report['successful_new_native_pages'] + extra_pages,
        new_finalized_prior_block_observations=report['new_finalized_prior_block_observations'] + extra_observations,
        private_data_unit_files_saved=report['private_data_unit_files_saved'] + extra_files,
        interrupted_evidence_fragments=evidence, unresolved_request_intents=1 + len(evidence),
        original_full_clock_audits_complete=False,
        incomplete_clock_scopes=['mempool_remaining_fifty_20261116_unit_12'] + [e['scope'] for e in evidence],
        successful_dispatch_subsets_verified=True, saved_pages_requested_again=0)
    write(campaign.CAMPAIGN / 'progress_verification.json', report)
    result = campaign.CAMPAIGN / 'RESULTS.md'
    result.write_text(result.read_text().replace(
        'All completed checkpoints pass data/clock audits and are privately saved.',
        'All saved data checkpoints pass reconstruction checks. The original full clock audits of interrupted units 12 and 13 remain incomplete; their known successful dispatches pass separately and both unknown intents remain explicit.'))
    print(__import__('json').dumps(report, indent=2)); return report


if __name__ == '__main__': verify()
