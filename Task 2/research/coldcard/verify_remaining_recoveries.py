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
    extension_path=campaign.CAMPAIGN/'supplemental_unit_21_selection.json'
    extension=None
    if extension_path.exists():
        extension=read(extension_path)
        selection_path=campaign.CAMPAIGN/'selection.json'
        assert extension['original_campaign_selection_sha256']==sha(selection_path)
        assert extension['unit']==21 and extension['source_ids']==['comparison_0157']
        assert extension['original_target_set_unchanged']
        def selection_read(path):
            value=read(path)
            if Path(path).resolve()==selection_path.resolve():
                assert len(value['units'])==20
                return dict(value,units=value['units']+[extension])
            return value
        original.read=selection_read
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
    if extension is not None:
        out=campaign.BASE/'mempool_remaining_fifty_20261116_unit_21'
        work=campaign.BASE/('source_cohort_work_'+out.name)
        q=read(out/'protocol.json');normalization=read(out/'audit_tape_normalization.json')
        assert q['inputs']['selection_extension']['sha256']==sha(extension_path)
        assert normalization['original_protocol_sha256']==sha(out/'protocol.json')
        assert normalization['original_provider_receipt_sha256']==sha(out/'run_receipt.json')
        metadata=read(out/'request_manifest.json.gz')
        fresh=[m for m in metadata if not m.get('offline_reused')]
        cached=[m for m in metadata if m.get('offline_reused')]
        pins=read(work/'cached_native_seed_manifest.json')['responses']
        assert len(cached)==len(pins)==13
        for pin in pins:
            source=work/'cache_seed'/'comparison_0157'/(pin['key']+'.json')
            assert sha(source)==pin['original_marker_sha256']
            expected=dict(read(source),offline_reused=True,reused_from_pass='mempool_remaining_fifty_20261116_unit_12',original_marker_sha256=pin['original_marker_sha256'])
            assert next(m for m in cached if m['key']==pin['key'])==expected
        tails=[m for m in fresh if m['key'].startswith('native_tail_')]
        assert len(fresh)<=q['maximum_requests']
        assert len(metadata)<=q['maximum_audit_tape_records']
        assert normalization['cached_responses_replayed']==13
        assert normalization['verified_tape_records']==len(metadata)
        assert len(tails)<=37 and 12+1+len(tails)<=50
        assert not {p['endpoint_sha256']for p in pins}.intersection(m['endpoint_sha256']for m in tails)
        assert normalization['actual_new_provider_requests']==len(fresh)
        report.update(supplemental_frozen_unit_sha256=sha(extension_path),
            original_selection_unchanged=True,original_fifty_target_set_unchanged=True,
            deferred_source_cached_responses_verified=13,deferred_source_original_unknown_intent_preserved=True)
    write(campaign.CAMPAIGN / 'progress_verification.json', report)
    result = campaign.CAMPAIGN / 'RESULTS.md'
    result.write_text(result.read_text().replace(
        'All completed checkpoints pass data/clock audits and are privately saved.',
        'All saved data checkpoints pass reconstruction checks. The original full clock audits of interrupted units 12 and 13 remain incomplete; their known successful dispatches pass separately and both unknown intents remain explicit.'))
    print(__import__('json').dumps(report, indent=2)); return report


if __name__ == '__main__': verify()
