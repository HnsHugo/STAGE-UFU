"""Document audited frontier recovery without counting old pages as new coverage."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def document(scope, library_id):
    scope = scope.resolve()
    base = scope.parent
    assert not (scope / 'RESULTS.md').exists()
    q = read(scope / 'protocol.json')
    a = read(scope / 'coverage_audit.json')
    v = read(scope / 'independent_verification.json')
    r = read(scope / 'continuation_reconciliation.json')
    receipt = read(scope / 'run_receipt.json')
    backup = read(scope / 'private_cache_backup.json')
    tests = read(scope / 'execution_validation.json')
    assert v['status'] == tests['status'] == 'passed'
    assert receipt['operational_locks_released'] and not backup['saved_privately']
    assert library_id.startswith('libfile_')
    assert r['recovered_pages_excluded_from_added_coverage']
    backup.update(saved_privately=True, library_file_id=library_id,
                  library_upload_status='succeeded', local_metadata_applied=True)
    write(scope / 'private_cache_backup.json', backup)
    if not (scope / 'collection_stop.json').exists():
        write(scope / 'collection_stop.json', dict(schema_version=1,
            status='normal_checkpoint_completion',
            reason='The twenty fixed outcomes are finalized; all incomplete histories remain retained.',
            stopped_at=datetime.now(timezone.utc).isoformat(),
            automatic_retry_performed=False, provider_or_route_changed=False))
    write(scope / 'final_execution_verification.json', dict(schema_version=1,
        status='passed', focused_tests=tests['tests'], new_recovery_guard_tests=tests['new_recovery_guard_tests'],
        protocol_input_pins_verified=read(scope / 'preparation_verification.json')['input_pins_verified'],
        successful_response_records_verified=a['all_successful_response_fingerprints_and_cursor_sequences_verified'],
        recovered_old_response_fingerprints_verified=r['recovered_old_responses_fingerprint_verified'],
        old_recovery_excluded_from_added_coverage=True, raw_tails_reextracted=a['new_raw_tails_reextracted'],
        new_vectors_independently_recounted=a['new_vectors_independently_recounted'],
        preceding_vectors_preserved=q['baseline_vectors'], retained_deep_queue_unchanged=True,
        model_fits=0, new_scores=0, final_view_sha256=r['final_view_sha256'],
        documentation_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    complete = r['new_complete_prefixes']
    bounded = len(r['bounded_incomplete_source_ids'])
    pending = len(r['pending_source_ids'])
    status = 'Completed and independently verified' if not pending else 'Interrupted; retained evidence independently verified'
    refusal = receipt['first_refusal_status']
    result = f'''# Verified fixed frontier recovery and extension

**{status}.** The fixed unit selected {r['selected']} source/reference pairs
from the untouched 16-page-bound queue, in frozen registry order. It completed
**{complete} new prior prefixes**, retains **{bounded} finalized incomplete
histories** and **{pending} unfinished sources**. Incomplete features stay null.
The three previous 576-page histories and every unselected row remain exact.

| Work in this unit | Verified count |
| --- | ---: |
| Fresh request intents | {r['fresh_request_intents']:,} |
| Fresh HTTP200 responses | {r['fresh_http_200']:,} |
| Old responses recovered against published fingerprints | {r['recovered_old_responses_fingerprint_verified']:,} |
| Old tail pages recovered | {r['recovered_old_tail_pages']:,} |
| Tail pages beyond the old 16-page bound | {r['fresh_tail_pages_beyond_old_bound']:,} |
| Recovered old source-transaction observations | {r['recovered_old_prior_block_observations']:,} |
| Additional source-transaction observations | {r['additional_source_transaction_observations']:,} |

Recovery is network work, not added coverage. The old reference and each old
tail body/endpoint had to match its published fingerprint before extension.
Observation counts are source/reference observations, not globally unique
transactions. No saved body was available for offline reuse in this unit.
The conservative request ceiling was {q['request_budget']['total_new_requests_at_most']:,}.
First refusal status: {refusal if refusal else 'none'}. No retry, route/provider
change, background automation, model fit or new score occurred.

Both audits pass: {a['all_successful_response_fingerprints_and_cursor_sequences_verified']:,}
successful response records and {a['new_raw_tails_reextracted']} raw tails verify.
All {complete} new vectors were independently recounted; every one of the
{q['baseline_vectors']:,} preceding vectors and all unselected rows is unchanged.
The {tests['tests']} focused tests pass, including {tests['new_recovery_guard_tests']}
new recovery/selection/collector-contract checks. Every prepared input pin
verifies. The private saved layer verifies {backup['private_files_verified']:,} files
and retains all 82 frozen private identities needed for subsequent units.

| Coverage | Available | Unavailable |
| --- | ---: | ---: |
| Coldcard / 1,500 fixed sources | {r['coldcard_vectors']:,} | {r['coldcard_unavailable_prefixes']} |
| CryptoBilis / 366 fixed sources | 329 | 37 |
| Overall / 1,866 fixed sources | {r['coldcard_vectors'] + 329:,} | {r['total_remaining_information_gaps']} |

The fourteen pre-reference-block predictors, cutoffs, operational
incident-membership target and unknown verified compromise/device labels remain
fixed. Comparisons are not proven legitimate. Full-current statuses remain
500 complete cases, 864 complete and 136 incomplete comparisons; these differ
from prior-prefix coverage. The expanded snapshot still has missing-prefix
bias and needs a fresh overlap check before any model work. No predictive theft
or hardware-wallet identification claim follows from these coverage results.

The saved private remaining_source_registry.json retains all 82 original
frontier identities and has a pinned fingerprint. Use it with this closed
resume checkpoint to prepare the next distinct scope; the original large
archive does not need to be retrieved again merely to recover these identities.
The one-time preparer and its old restoration report remain immutable.

Next: {'finish the unfinished selected sources in a distinct pinned successor after the live access/cooldown checks' if pending else 'select the next at-most-twenty untouched IDs in existing registry order'}.
The {bounded} newly bounded histories, the exact three 576-page cursors and all
other missing IDs remain retained in their separate queues. There are
{r['remaining_previously_unselected_16_page_sources']} untouched 16-page IDs left.
Require fresh historical/local locks, live policy/cooldown, exact running lease
publication/readback and one normal original-route counter HTTP200. Stop new
starts at the first refusal. Routine replies omit archives.
'''
    (scope / 'RESULTS.md').write_text(result)
    (scope / 'README.md').write_text('# Fixed frontier recovery and extension: twenty source/reference pairs\n\n'
        + '**' + status + '.** See [RESULTS.md](RESULTS.md).\n\n'
        + 'The approved protocol, frozen source order, explicit old-body recovery\n'
          'fingerprints and private evidence layer are preserved. Original refusals\n'
          'and prelaunch review history remain immutable. No fit or score.\n')
    review = scope / 'REVIEW.md'
    review.write_text('**Historical prelaunch review.** Publication was explicitly approved and\n'
        'completed. The current outcome is in [RESULTS.md](RESULTS.md).\n\n' + review.read_text())
    entry = f'''**Latest verified frontier unit - 12 November 2026**

[The fixed twenty-source unit](research/coldcard/{scope.name}/RESULTS.md)
completed {complete} new prior prefixes and retains {bounded} finalized incomplete
histories and {pending} unfinished sources. It made {r['fresh_request_intents']:,} fresh
requests ({r['fresh_http_200']:,} HTTP200); {r['recovered_old_responses_fingerprint_verified']:,}
old response fingerprints verify. The {r['recovered_old_tail_pages']} recovered old tail
pages are excluded from added coverage. The unit added
{r['additional_source_transaction_observations']:,} source-transaction observations,
not globally unique transactions. Both audits and {tests['tests']} focused checks pass;
all {q['baseline_vectors']:,} preceding vectors, unselected rows and three 576-page
histories verify. The private evidence is saved. Coldcard now has
{r['coldcard_vectors']:,}/1,500 vectors; CryptoBilis stays 329/366, with
{r['total_remaining_information_gaps']} information gaps overall. Fourteen definitions,
cutoffs, unknown theft/device labels, full-current statuses and historical
models/scores stay fixed. No fit, score, retry, fallback or automation ran.

Next: {'finish only the unfinished selected IDs in a distinct bounded successor after the live cooldown' if pending else 'the next at-most-twenty of the '+str(r['remaining_previously_unselected_16_page_sources'])+' untouched 16-page IDs, in frozen registry order'}.
Retain every deeper queue and missing row; never select a completed source.
Use saved identities/pages, fresh locks/live policy/lease/cooldown, exact running
lease readback, one original-route counter HTTP200 and first-refusal stop.
Recheck overlap before updated-snapshot models. Collection is closed, the lease
is idle, locks are free and automation disabled. This supersedes prelaunch
approval blockers and older next-unit suggestions; their history is retained.

'''
    for name in ['AGENTS.md', 'ALIGNMENT.md', 'PROJECT_STATUS.md']:
        p = base.parents[1] / name
        head, rest = p.read_text().split('\n\n', 1)
        p.write_text(head + '\n\n' + entry + rest)
    return dict(scope=scope.name, new_complete_prefixes=complete,
        coldcard_vectors=r['coldcard_vectors'], pending=pending,
        remaining_information_gaps=r['total_remaining_information_gaps'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scope', type=Path)
    parser.add_argument('library_id')
    args = parser.parse_args()
    print(json.dumps(document(args.scope, args.library_id), sort_keys=True))
