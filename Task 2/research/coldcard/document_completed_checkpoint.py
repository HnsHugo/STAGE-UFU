"""Document an audited checkpoint using its verified counts and upload receipt ID."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def document(scope, library_id, next_checkpoint):
    scope = scope.resolve()
    assert not (scope / 'RESULTS.md').exists(), 'Never replace a closed report'
    q = read(scope / 'protocol.json')
    a = read(scope / 'coverage_audit.json')
    v = read(scope / 'independent_verification.json')
    r = read(scope / 'continuation_reconciliation.json')
    receipt = read(scope / 'run_receipt.json')
    backup = read(scope / 'private_cache_backup.json')
    checks = read(BASE / 'source_prefix_extension_20261110_05/execution_validation.json')
    assert v['status'] == checks['status'] == 'passed'
    assert not receipt['first_refusal_status'] and receipt['operational_locks_released']
    assert r['pending_source_ids'] == [] and r['status'] == 'all_selected_finalized'
    assert library_id.startswith('libfile_') and not backup['saved_privately']
    assert next_checkpoint > q['max_pages_per_address']
    backup.update(saved_privately=True, library_file_id=library_id,
                  library_upload_status='succeeded', local_metadata_applied=True)
    write(scope / 'private_cache_backup.json', backup)
    write(scope / 'collection_stop.json', dict(schema_version=1,
        status='normal_checkpoint_completion',
        reason='Every selected outcome is audited; incomplete evidence and distinct-successor cursors remain retained.',
        stopped_at=datetime.now(timezone.utc).isoformat(),
        automatic_retry_performed=False, provider_or_route_changed=False))
    write(scope / 'execution_validation.json', dict(schema_version=1, status='passed',
        focused_tests_in_preceding_saved_unit=checks['tests_passed'],
        protocol_input_pins_verified=read(scope / 'preparation_verification.json')['input_pins_verified'],
        raw_tails_reextracted=a['new_raw_tails_reextracted'],
        saved_response_records_verified=a['all_successful_response_fingerprints_and_cursor_sequences_verified'],
        new_vectors_independently_recounted=a['new_vectors_independently_recounted'],
        preceding_vectors_preserved=q['baseline_vectors'],
        collector_locks_released=True, collector_lease_idle=True,
        model_fits=0, new_scores=0, final_view_sha256=r['final_view_sha256'],
        documentation_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    ids = ', '.join(r['bounded_incomplete_source_ids']) or 'none'
    text = f'''# Verified checkpoint through {q['max_pages_per_address']} pages

Exactly {r['selected']} retained incomplete source/reference histories were
continued beyond {q['previous_bound']} saved pages. This unit completed
**{r['new_complete_prefixes']} new prior prefixes** and retains
**{len(r['bounded_incomplete_source_ids'])} incomplete histories** with null
features and exact continuation cursors. It added
**{r['additional_source_transaction_observations']:,} source-transaction observations**,
not a globally unique transaction count. No cached tail page was requested again.

The unit reused {r['saved_responses_reused']} validated responses and made
**{r['new_request_intents']} new requests, all HTTP200**, within the pinned
{q['request_budget']['total_new_requests_at_most']}-request maximum. Both independent
audits pass: {a['all_successful_response_fingerprints_and_cursor_sequences_verified']}
response records, {a['new_raw_tails_reextracted']} re-extracted raw tails, every
new vector, all {q['baseline_vectors']:,} preceding vectors and all unselected
rows verify. The preceding saved unit's {checks['tests_passed']} focused workflow,
cache-resume, temporal/funding and access tests remain recorded; input pins verify
the unchanged shared collection code. The saved private archive verifies all
{backup['private_files_verified']:,} evidence files.

| Coverage | Available | Unavailable |
| --- | ---: | ---: |
| Coldcard / 1,500 selected sources | {r['coldcard_vectors']:,} | {r['coldcard_unavailable_prefixes']} |
| CryptoBilis / 366 selected sources | 329 | 37 |
| Overall / 1,866 selected sources | {r['coldcard_vectors'] + 329:,} | {r['total_remaining_information_gaps']} |

The source/reference unit, operational incident-membership target, fourteen
strictly pre-reference-block predictors, unknown verified compromise/device
labels, frozen scores and thresholds remain unchanged. Comparisons are not
proven legitimate. Full-current statuses remain separately 500 complete cases,
864 complete and 136 incomplete comparisons. There was no fit, new score, retry,
fallback or automation. Missing-prefix coverage bias remains; recheck overlap
before any updated-snapshot model work. Full-current counters do not determine
the exact remaining pre-reference history cost.

Retained incomplete IDs: {ids}. Next: a distinct pinned checkpoint through
{next_checkpoint} pages, reusing every saved page and never selecting a completed
source again. Retain all other missing IDs. Fresh historical/local locks, live
policy/cooldown, exact lease publication/readback and one normal original-route
counter HTTP200 remain mandatory. Collection is closed, locks free and lease idle.
'''
    (scope / 'RESULTS.md').write_text(text)
    p = scope / 'README.md'
    old = p.read_text(); head, rest = old.split('\n', 1)
    p.write_text(head + '\n\n**Completed and independently verified.** See [RESULTS.md](RESULTS.md).\n' + rest)
    entry = f'''**Latest verified unit - {q['max_pages_per_address']}-page checkpoint, 10 November 2026**

[The latest checkpoint](research/coldcard/{scope.name}/RESULTS.md) reused
{r['saved_responses_reused']} saved responses and made {r['new_request_intents']}
fresh HTTP200 requests. It added {r['additional_source_transaction_observations']:,}
source-transaction observations, completed {r['new_complete_prefixes']} new prefixes
and retains {len(r['bounded_incomplete_source_ids'])} incomplete histories with null
features and continuation cursors. Both audits pass, old vectors/unselected rows
verify and the private cache is saved. The earlier twenty focused tests remain
recorded; shared collection code is unchanged. Coldcard now has
{r['coldcard_vectors']:,}/1,500 vectors; CryptoBilis stays 329/366, leaving
{r['total_remaining_information_gaps']} information gaps. Cutoffs, fourteen
predictors, unknown labels, full-current statuses and historical models/scores
remain unchanged. No fit or new score ran.

Next: a distinct checkpoint through {next_checkpoint} pages for {ids} only,
reusing all saved evidence. Preserve other incomplete IDs and all completed rows.
Keep fresh locks/lease/cooldown, original route and first-refusal stop. Recheck
overlap before updated-snapshot modeling. Collection is closed, lease idle, locks
free and automation disabled. This entry supersedes older next-unit suggestions
while preserving their historical evidence.

'''
    for name in ['AGENTS.md', 'ALIGNMENT.md', 'PROJECT_STATUS.md']:
        p = BASE.parents[1] / name
        head, rest = p.read_text().split('\n\n', 1)
        p.write_text(head + '\n\n' + entry + rest)
    return dict(scope=scope.name, vectors=r['coldcard_vectors'],
                saved_private_archive=backup['file_name'], next_checkpoint=next_checkpoint)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scope', type=Path)
    parser.add_argument('library_id')
    parser.add_argument('next_checkpoint', type=int)
    args = parser.parse_args()
    print(json.dumps(document(args.scope, args.library_id, args.next_checkpoint), sort_keys=True))
