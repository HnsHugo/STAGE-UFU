"""Recover a hashed CryptoBilis source registry and prescoring contract offline.

No provider HTTP, source-history collection, comparison sampling, scoring or fit.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'coldcard'))
from collect_theft_seeds import check_history


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def hashed(text):
    return sha(text.encode())


def encoded(data):
    return (json.dumps(data, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def pinned(pin):
    path = (ROOT/pin['file']).resolve()
    require(path.is_relative_to(ROOT), 'Input outside research root')
    require(sha(path.read_bytes()) == pin['sha256'], 'Fingerprint mismatch: '+pin['file'])
    return path


def sat(value):
    require(type(value) is int and value >= 0, 'Invalid integer satoshi value')
    return value


def validate_payment(tx, blocks):
    status = tx['status']
    require(status.get('confirmed') is True and status.get('block_height') in blocks, 'Unconfirmed/out-of-scope reference')
    anchor = blocks[status['block_height']]
    require(status.get('block_hash') == anchor['hash'] and status.get('block_time') == anchor['time'], 'Reference block anchor mismatch')
    require(re.fullmatch('[0-9a-f]{64}', tx['txid']), 'Invalid reference TXID')
    require(tx['vin'] and tx['vout'], 'Empty reference inputs/outputs')
    for vin in tx['vin']:
        prevout = vin.get('prevout')
        require(prevout and isinstance(prevout.get('scriptpubkey_address'), str) and prevout['scriptpubkey_address'], 'Unresolved source address')
        require(re.fullmatch('[0-9a-f]{64}', vin['txid']) and type(vin['vout']) is int and vin['vout'] >= 0, 'Invalid funding outpoint')
    require(sum(sat(v['prevout']['value']) for v in tx['vin']) - sum(sat(v['value']) for v in tx['vout']) == sat(tx['fee']), 'Reference input/output/fee mismatch')


def recover(histories, refs, anchors, start, end):
    blocks = {b['height']: b for b in anchors}
    collectors = {r['address'] for r in refs}
    payments, outside, outside_payments, checks = {}, set(), set(), []
    for ref in refs:
        history = histories[ref['address']]
        require(history['address'] == ref['address'] and history['provider'] == 'https://blockstream.info/api', 'Collector/provider mismatch')
        check = check_history(ref['address'], history['transactions'], history['before'], history['after'], history['audit']['pagination_exhausted'])
        require(check == history['audit'] and check['coverage_complete_by_provider_counters'], 'Collector history does not reconcile')
        count = 0
        for tx in history['transactions']:
            if not any(o.get('scriptpubkey_address') == ref['address'] and sat(o['value']) > 0 for o in tx['vout']):
                continue
            if not start <= tx['status']['block_time'] < end:
                outside_payments.add(tx['txid'])
                outside.update(v['prevout']['scriptpubkey_address'] for v in tx['vin'] if v.get('prevout') and v['prevout'].get('scriptpubkey_address'))
                continue
            validate_payment(tx, blocks)
            require(not {v['prevout']['scriptpubkey_address'] for v in tx['vin']} & collectors, 'Collector self-input is not a source candidate')
            if tx['txid'] in payments:
                require(payments[tx['txid']]['tx'] == tx, 'Ambiguous collector transaction')
                payments[tx['txid']]['collectors'].add(ref['address'])
            else:
                payments[tx['txid']] = dict(tx=tx, collectors={ref['address']})
            count += 1
        checks.append(dict(collector_sha256=hashed(ref['address']), event_payments=count,
                           history_transactions=len(history['transactions']), provider_counters_reconciled=True,
                           cryptographic_inclusion_verified=False))
    grouped, evidence, outpoints = defaultdict(list), [], set()
    for txid,item in sorted(payments.items()):
        tx = item['tx']
        for address in {v['prevout']['scriptpubkey_address'] for v in tx['vin']}:
            grouped[address].append(item)
        for index,vin in enumerate(tx['vin']):
            point = f"{vin['txid']}:{vin['vout']}"
            require(point not in outpoints, 'Repeated spent outpoint')
            outpoints.add(point)
            evidence.append(dict(reference_txid_sha256=hashed(txid), input_index=index,
                                 address_sha256=hashed(vin['prevout']['scriptpubkey_address']),
                                 funding_txid_sha256=hashed(vin['txid']), funding_vout=vin['vout'],
                                 outpoint_sha256=hashed(point), observed_input_value_sat=vin['prevout']['value'],
                                 block_height=tx['status']['block_height'], block_hash=tx['status']['block_hash']))
    rows = []
    for number,address in enumerate(sorted(grouped, key=lambda a:(hashed(a),a)),1):
        items = sorted(grouped[address], key=lambda x:(x['tx']['status']['block_height'],x['tx']['txid']))
        first = items[0]['tx']
        rows.append(dict(source_id=f'cryptobilis_source_{number:04d}', address_sha256=hashed(address),
                         reference_txid_sha256=hashed(first['txid']), reference_payment_hashes=[hashed(x['tx']['txid']) for x in items],
                         collector_sha256=sorted({hashed(c) for x in items for c in x['collectors']}),
                         cutoff_height=first['status']['block_height'], cutoff_block_hash=first['status']['block_hash'],
                         incident_group='cryptobilis_2026', case_relation='graph_candidate',
                         observed_role='input_source_to_historically_attributed_collection_reference',
                         cryptobilis_reference_source_membership=1,
                         labels=dict(independently_verified_compromise=None, independently_verified_seed_origin=None,
                                     hardware_signing_at_event=None, reported_loss=None, reported_hardware_association=None),
                         reference_input_count=sum(v['prevout']['scriptpubkey_address'] == address for x in items for v in x['tx']['vin']),
                         features=None, prior_prefix_status='not_collected_in_this_unit'))
    audit = dict(reference_payments=len(payments), source_candidates=len(rows), input_observations=len(evidence),
                 multi_input_payments=sum(len(x['tx']['vin'])>1 for x in payments.values()),
                 multi_address_payments=sum(len({v['prevout']['scriptpubkey_address'] for v in x['tx']['vin']})>1 for x in payments.values()),
                 observed_reference_input_value_sat=sum(e['observed_input_value_sat'] for e in evidence),
                 observed_reference_fees_sat=sum(x['tx']['fee'] for x in payments.values()),
                 outside_window_payments=len(outside_payments), outside_window_sources=len(outside),
                 outside_window_source_overlap=len(outside & set(grouped)),
                 source_blocks={str(k):v for k,v in sorted(Counter(r['cutoff_height'] for r in rows).items())},
                 collector_checks=checks)
    return rows,evidence,audit,outside


def development_references(protocol_path, view):
    protocol = read(protocol_path)
    root, checkpoints, pins = protocol_path.parent.parent, {}, []
    for key in sorted(set(protocol['checkpoints'].values())):
        pin = protocol['inputs'][key]
        path = root/pin['file']
        require(sha(path.read_bytes()) == pin['sha256'], 'Coldcard checkpoint fingerprint mismatch')
        checkpoints[key] = read(path)['entries']
        pins.append(dict(file=str(path.relative_to(ROOT)),sha256=pin['sha256']))
    references = set()
    for row in view['rows']:
        if row['features'] is None:
            continue
        name = row.get('precutoff_history_provenance',{}).get('pass_name',row['full_history_provenance']['chosen_pass'])
        entry = checkpoints[protocol['checkpoints'][name]][row['source_id']]
        require(entry['address_sha256'] == row['address_sha256'] and entry['features'] == row['features'], 'Coldcard evidence join mismatch')
        references.update(t['transaction_id'] for t in entry['prefix'])
    return references,pins


def build(config_path):
    config = read(config_path)
    paths = {k:pinned(v) for k,v in config['inputs'].items()}
    require(paths['builder'] == Path(__file__).resolve(), 'Wrong builder implementation')
    central,registry = read(paths['central']),read(paths['role_registry'])
    refs = [r for r in central['references'] if r['case_group']=='cryptobilis_2026']
    anchors = [b for b in central['blocks'] if b['case_group']=='cryptobilis_2026']
    require(len(refs)==len(anchors)==2, 'Changed collector/block scope')
    histories = {}
    for i,ref in enumerate(refs):
        roles = [r for r in registry['records'] if r['address']==ref['address'] and r['role']=='collection' and r['include_in_pilot']]
        require(len(roles)==1 and roles[0]['hardware_control']=='unknown', 'Role/evidence scope changed')
        path = paths['collector_'+str(i)]
        require(sha(path.read_bytes())==ref['history_sha256'], 'Central collector fingerprint mismatch')
        histories[ref['address']] = read(path)
    window = config['event_window']
    start,end = [int(datetime.fromisoformat(window[k]).timestamp()) for k in ('start_utc','end_exclusive_utc')]
    require(start<end, 'Invalid event window')
    rows,evidence,audit,outside = recover(histories,refs,anchors,start,end)
    require({k:audit[k] for k in config['expected_counts']}==config['expected_counts'], 'Changed observed source scope')
    view,model,model_protocol = [read(paths[k]) for k in ('coldcard_view','frozen_model','frozen_model_protocol')]
    require(len(view['rows'])==1500 and model['target']=='known_coldcard_core_membership' and model['fit_partition']=='train', 'Wrong development model/universe')
    require(model['parameters']==model_protocol['estimator_parameters'], 'Frozen model parameters changed')
    old_refs,checkpoint_pins = development_references(paths['feasibility_protocol'],view)
    old_addresses = {r['address_sha256'] for r in view['rows']}
    old_payments = {r['payment_txid_sha256'] for r in view['rows']}
    addresses = {r['address_sha256'] for r in rows}
    payments = {r['reference_txid_sha256'] for r in rows}
    funding = {e['funding_txid_sha256'] for e in evidence}
    audit['partial_overlap_audit'] = dict(exact_development_address_hashes=sorted(old_addresses & addresses),
        exact_development_reference_hashes=sorted(old_payments & payments),
        direct_funding_vs_completed_development_prior_hashes=sorted(funding & old_refs),
        completed_development_prior_references=len(old_refs), observed_direct_funding_transactions=len(funding),
        full_source_prefix_overlap_status='pending; direct funding observations are not complete source histories')
    cold_ref = next(r for r in central['references'] if r['case_group']=='coldcard_2026')
    cold = read(paths['coldcard_collector'])
    require(sha(paths['coldcard_collector'].read_bytes())==cold_ref['history_sha256'], 'Coldcard collector fingerprint mismatch')
    adjacent = {hashed(v['prevout']['scriptpubkey_address']) for tx in cold['transactions']
                if any(o.get('scriptpubkey_address')==cold_ref['address'] and o['value']>0 for o in tx['vout'])
                for v in tx['vin'] if v.get('prevout') and v['prevout'].get('scriptpubkey_address')}
    excluded = old_addresses | adjacent | addresses | {hashed(a) for a in outside}
    excluded |= {hashed(r['address']) for r in central['references']} | {hashed(r['address']) for r in registry['records']}
    protocol = deepcopy(config['transfer_contract'])
    require(protocol['operational_target']=='cryptobilis_reference_source_membership' and
            protocol['threshold']==model['threshold']==.5 and protocol['threshold_operator']=='>=', 'Wrong target/threshold contract')
    require(protocol['comparison_selection']['quotas']==[
        dict(height=int(h),case_sources=n,desired_comparisons=2*n) for h,n in audit['source_blocks'].items()], 'Comparison quotas differ from source strata')
    protocol.update(schema_version=1,pass_name=config['pass_name'],created_at=config['created_at'],input_commit=config['input_commit'],
                    event_window=window,blocks=anchors,predictor_allowlist=model_protocol['predictor_allowlist'],
                    frozen_model=config['inputs']['frozen_model'],frozen_model_protocol=config['inputs']['frozen_model_protocol'],
                    can_score_primary_transfer=False,source_vectors_available=0,comparison_sources_selected=0,
                    scored_rows=0,model_fits=0,provider_requests=0,automation_created=False)
    protocol['comparison_selection']['excluded_address_sha256'] = sorted(excluded)
    audit.update(source_vectors_available=0,comparison_sources_selected=0,
                 comparisons_planned=sum(q['desired_comparisons'] for q in protocol['comparison_selection']['quotas']),
                 verified_compromise_labels=0,verified_device_labels=0,source_mapped_owner_reports=0,
                 source_refresh=config['source_refresh'],scored_rows=0,model_fits=0,provider_requests=0,
                 full_history_claim='Two collector snapshots reconcile; no individual source-history coverage is claimed.',
                 frozen_model_sha256=sha(paths['frozen_model'].read_bytes()),old_registry_flags_unchanged=True)
    files={'source_registry.json.gz':gzip.compress(encoded(dict(schema_version=1,rows=rows)),mtime=0),
           'input_evidence.json.gz':gzip.compress(encoded(evidence),mtime=0),
           'scope_audit.json':encoded(audit),'transfer_protocol.json':encoded(protocol)}
    files['README.md']=report(config,audit,protocol).encode()
    files['verification.json']=encoded(dict(configuration_sha256=sha(config_path.read_bytes()),inputs=config['inputs'],
        additional_development_checkpoint_pins=checkpoint_pins,outputs_sha256={k:sha(v) for k,v in files.items()},
        verified_reference_payments=audit['reference_payments'],verified_sources=len(rows),verified_input_observations=len(evidence),
        actual_comparisons=0,actual_source_vectors=0,model_fits=0,provider_requests=0,scores_computed=0))
    return files,audit


def report(config,audit,protocol):
    overlap=audit['partial_overlap_audit']
    lines=['# CryptoBilis source readiness and transfer contract','',
        'This completed offline unit recovers hashed source evidence and prespecifies a future structural-proxy transfer study. It performs no blockchain-provider HTTP, source-history collection, comparison sampling, scoring or model fit. The earlier PROGRESS.md is a preserved recovery checkpoint; this report and verification.json are the completed unit.','',
        '## Actual recovered evidence','',
        f"The two pinned collector snapshots yield {audit['reference_payments']} event payments, {audit['source_candidates']} unique decoded input sources and {audit['input_observations']} consumed outpoints on 9 October 2026 UTC. There are {audit['multi_input_payments']} multi-input payments, {audit['multi_address_payments']} multi-address payments and seven outside-window receipts from one additional source. The event sources have no overlap with that outside-window source. Both collectors and the unresolved participant narrative belong to one incident, not separate test cases.",'',
        f"Reference input values total {audit['observed_reference_input_value_sat']} sat and fees total {audit['observed_reference_fees_sat']} sat. These are measured provider-record amounts, not certified stolen totals or predictors. Reference height/hash/time and input/output/fee closure verify; both collector histories reconcile stable saved provider counters. No cryptographic inclusion proof or complete individual source-history claim is made.",'',
        'Every source has case_relation=graph_candidate. Verified compromise, seed/device identity and source-mapped owner reports remain unknown. Collector attribution comes from the historical Bitquery-derived registry; the professor reference review already confirms CryptoBilis as the intended second incident. The old provisional flags are preserved. Current access to the Bitquery page failed through the web reader; no new source contents or labels are claimed. The Exame participant narrative remains unmapped.','',
        '## Overlap and current gates','',
        f"Exact overlap with 1,500 Coldcard development addresses: {len(overlap['exact_development_address_hashes'])}. Exact reference-payment overlap: {len(overlap['exact_development_reference_hashes'])}. The {overlap['observed_direct_funding_transactions']} observed funding TXIDs have {len(overlap['direct_funding_vs_completed_development_prior_hashes'])} matches against {overlap['completed_development_prior_references']} completed Coldcard prior references. This is a partial funding audit; full source prefixes and controls are not available, so complete cross-development overlap and entity independence remain unresolved.",'',
        '**Actual source vectors: 0. Actual selected comparisons: 0. Actual scores: 0. No new F1.** The Coldcard F1 remains its original single-incident result. The registry is ready; primary external scoring is blocked by the pending census, features and complete overlap audit.','',
        '## Frozen future design','',
        '| Reference block | Source candidates | Planned comparisons |','| --- | ---: | ---: |']
    lines += [f"| {q['height']} | {q['case_sources']} | {q['desired_comparisons']} |" for q in protocol['comparison_selection']['quotas']]
    lines += ['',
        'The external target is cryptobilis_reference_source_membership, an explicitly named incident-specific graph proxy. The hypothesis tests transport of the frozen Coldcard profile. Do not rename old known_coldcard_core_membership labels or infer verified theft/device labels. A complete two-block input census precedes deterministic 2:1 same-period comparison selection, fixed before scores. Prior development addresses, known case-adjacent sources/collectors, outside-window sources and the unresolved third registry recipient are excluded. No balance/age/fee/model-score/history-success selection or replacement.','',
        'Use the same fourteen definitions, strict height < reference-block cutoff, original route/verified TLS and validated reference/funding/terminal-exhaustion checks. Reuse only exported Coldcard training medians and fixed missing indicators. Keep the tree, >=0.5 threshold, weights and seed unchanged. Keep the entire CryptoBilis incident outside fitting. Retain/quarantine measured components spanning development and external data, reporting attrition without replacement; never split a linked group to rescue a score. Require at least 20 eligible case and 20 comparison vectors for the primary complete-case analysis. Compare to fixed constant, inactivity and balance rankings.','',
        'CryptoBilis was already inspected in recipient/transaction work. Future whole-incident evaluation is exploratory proxy transport, not an untouched, prospective or verified theft/device test. Distinct windows do not establish independent people/devices. No source-level victim list, new network collector or automation is created.','',
        '## Saved files and next unit','',
        'source_registry.json.gz contains hashed source/reference rows, unknown labels and null features. input_evidence.json.gz contains the hashed outpoint observations. scope_audit.json and verification.json retain reconciled counts, partial overlaps, fingerprints and the source-access limit. transfer_protocol.json fixes target mapping, comparisons, preparation, overlap policies and readiness gates. Raw address lists/private caches are not republished.','',
        'The next executable unit is the anchored two-block input census and fixed comparison selection, then a separately pinned bounded prefix collection. Before any provider HTTP, check lease, local lock, due time and Retry-After; preserve the original provider/route/TLS and refusal policy. The collection plan remains disabled in this readiness unit.','',
        'From Task 2/research/external_cases:','', '```sh',
        f"python build_cryptobilis_source_protocol.py verify {config['pass_name']}/configuration.json",
        'python -m unittest test_cryptobilis_source_protocol','```','',
        'Sources: [historical collector roles](../hardware_case_registry_20261019.json), [professor review](../PROFESSOR_REFERENCES.md), [central anchors](../central_protocol_20261020.json), [Coldcard study](../../../source_address_study/README.md).','']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['build','verify'])
    parser.add_argument('configuration',type=Path)
    args=parser.parse_args();path=args.configuration.resolve();files,audit=build(path)
    for name,data in files.items():
        out=path.parent/name
        if args.mode=='build':
            require(not out.exists(),'Refusing to overwrite a completed readiness output')
            out.write_bytes(data)
        else:
            require(out.read_bytes()==data,'Readiness output differs: '+name)
    print(json.dumps(dict(mode=args.mode,sources=audit['source_candidates'],reference_payments=audit['reference_payments'],
                         input_observations=audit['input_observations'],planned_comparisons=audit['comparisons_planned'],
                         actual_comparisons=0,actual_vectors=0,model_fits=0,provider_requests=0)))


if __name__=='__main__':
    main()
