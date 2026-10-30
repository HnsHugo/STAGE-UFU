"""Audit a pinned comparison design and select same-block input sources offline."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import sys

from build_source_registry import artifacts, digest, json_bytes
from prepayment_pilot import FEATURE_NAMES
import source_cohort as cohort

sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'external_cases'))
from rank_block_recipients import coinbase, validate_block


def load_design(path):
    protocol = json.loads(path.read_bytes())
    root = path.parent.parent
    loaded = {}
    for name, pin in protocol['inputs'].items():
        raw = (root/pin['file']).read_bytes()
        if digest(raw) != pin['sha256']:
            raise ValueError('Design input checksum mismatch: '+name)
        if name != 'block_validator':
            loaded[name] = json.loads(gzip.decompress(raw) if name=='source_view' else raw)
    view = loaded['source_view']
    _, records = cohort.plan(root/protocol['inputs']['cohort_protocol']['file'])
    cohort.validate(loaded['checkpoint'], root/protocol['inputs']['cohort_protocol']['file'], records)
    if (view['protocol_sha256'] != protocol['inputs']['source_view_protocol']['sha256']
            or protocol['predictors'] != list(FEATURE_NAMES)
            or view['predictor_allowlist'] != list(FEATURE_NAMES)):
        raise ValueError('Predictor view/protocol mismatch')
    case = {r['source_id']:r for r in view['rows']}
    if len(case)!=len(view['rows']) or set(case)!=set(loaded['checkpoint']['entries']) or len(case)!=500:
        raise ValueError('Case cohort coverage mismatch')
    for record in records:
        row = case[record['pilot_id']]
        if (row['address_sha256']!=record['address_sha256']
                or row['payment_txid_sha256']!=digest(record['payment_txid'].encode())
                or row['cutoff_height']!=record['cutoff_height']
                or row['features']!=loaded['checkpoint']['entries'][record['pilot_id']]['features']
                or row['case_evidence']['case_relation']!='source_attributed'):
            raise ValueError('Case identity/features/evidence mismatch')
    blocks = [b for b in loaded['block_protocol']['blocks'] if b['case_group']==protocol['incident_group']]
    if protocol['blocks'] != blocks:
        raise ValueError('Block selection differs from pinned incident window')
    counts = Counter(r['cutoff_height'] for r in view['rows'])
    expected = [dict(height=h,case_sources=n,comparison_quota=2*n) for h,n in sorted(counts.items())]
    selection = protocol['comparison_selection']
    if (selection['ratio_per_case']!=2 or selection['maximum_sources']!=1000
            or selection['quotas']!=expected or protocol['case_source_count']!=500):
        raise ValueError('Comparison quotas changed')
    files, _ = artifacts(root/protocol['inputs']['registry_protocol']['file'])
    excluded = {r['address'] for r in json.loads(files['addresses.json'])['records']}
    excluded.add(loaded['registry_protocol']['collector_address'])
    return protocol, loaded, records, excluded


def census(blocks, references):
    if len(blocks)!=len(references) or len({b['height'] for b in blocks})!=len(blocks):
        raise ValueError('Incomplete/repeated block set')
    expected = {r['height']:r for r in references}
    first, transactions, stats = {}, {}, []
    for block in sorted(blocks,key=lambda b:b['height']):
        if block['height'] not in expected:
            raise ValueError('Block outside design')
        validate_block(block, expected[block['height']])
        missing = addressed = 0
        for tx in sorted(block['tx'],key=lambda t:t['hash']):
            if tx['hash'] in transactions:
                raise ValueError('Transaction repeated across blocks')
            transactions[tx['hash']] = (block['height'],tx)
            if coinbase(tx):
                continue
            for vin in tx['inputs']:
                prevout = vin.get('prev_out') or {}
                value = prevout.get('value')
                if type(value) is not int or value < 0:
                    raise ValueError('Missing/invalid prevout value')
                address = prevout.get('addr')
                if not isinstance(address,str) or not address:
                    missing += 1
                    continue
                if value == 0:
                    continue
                addressed += 1
                first.setdefault(address,dict(address=address,cutoff_height=block['height'],
                    cutoff_block_hash=block['hash'],reference_txid=tx['hash']))
        stats.append(dict(height=block['height'],decoded_positive_input_observations=addressed,
                          unresolved_address_input_observations=missing,transaction_count=len(block['tx'])))
    return first, transactions, stats


def check_case_anchors(records, case_rows, transactions):
    case = {r['source_id']:r for r in case_rows}
    for record in records:
        if record['payment_txid'] not in transactions:
            raise ValueError('Case payment missing from block census')
        height, tx = transactions[record['payment_txid']]
        inputs = [i['prev_out'] for i in tx['inputs']
                  if (i.get('prev_out') or {}).get('addr')==record['address']]
        evidence = case[record['pilot_id']]['event_evidence']
        if (height!=record['cutoff_height'] or not inputs
                or len(inputs)!=evidence['observed_input_count']
                or sum(i['value'] for i in inputs)!=evidence['observed_input_value_sat']):
            raise ValueError('Case source/amount/count does not reconcile across providers')


def choose(first, excluded, quotas, prefix):
    selected, strata = [], []
    if len({q['height'] for q in quotas})!=len(quotas):
        raise ValueError('Repeated quota stratum')
    grouped = defaultdict(list)
    for address, row in first.items():
        if address not in excluded:
            grouped[row['cutoff_height']].append(row)
    for quota in quotas:
        height, cap = quota['height'],quota['comparison_quota']
        if type(cap) is not int or cap<0:
            raise ValueError('Invalid source quota')
        pool = sorted(grouped[height],key=lambda r:(digest((prefix+r['address']).encode()),r['address']))
        take = pool[:cap]
        selected.extend(take)
        strata.append(dict(height=height,eligible_sources=len(pool),quota=cap,
                           selected_sources=len(take),shortfall=max(0,cap-len(take))))
    return selected, strata


def audit(path, cache):
    protocol, loaded, records, excluded = load_design(path)
    metadata = {b['height']:b for b in loaded['block_summary']['blocks']}
    cache_rows = []
    for block in protocol['blocks']:
        file = cache/(str(block['height'])+'.json')
        cache_rows.append(dict(height=block['height'],file=str(block['height'])+'.json',
            present=file.is_file(),historical_raw_sha256=metadata[block['height']]['raw_json_sha256']))
    return dict(schema_version=1,protocol_sha256=digest(path.read_bytes()),design_valid=True,
                case_sources=len(records),predictor_count=len(protocol['predictors']),
                case_sources_and_comparison_quotas=protocol['comparison_selection']['quotas'],
                excluded_known_related_addresses=len(excluded),
                required_block_cache=cache_rows,available_block_files=sum(r['present'] for r in cache_rows),
                complete_input_census_performed=False,comparison_population_size=None,
                comparisons_selected=False,comparison_histories_collected=False,
                split_created=False,model_fitted=False,
                next_action='Recover or acquire the four anchored complete blocks, then run select. Hash and validate each snapshot; do not substitute output-recipient tables or create synthetic controls.')


def select(path, cache, include_census=False):
    protocol, loaded, records, excluded = load_design(path)
    blocks, snapshots = [], []
    historical = {b['height']:b for b in loaded['block_summary']['blocks']}
    for ref in protocol['blocks']:
        raw = (cache/(str(ref['height'])+'.json')).read_bytes()
        blocks.append(json.loads(raw))
        snapshots.append(dict(height=ref['height'],sha256=digest(raw),bytes=len(raw),
            matches_historical_bytes=digest(raw)==historical[ref['height']]['raw_json_sha256']))
    first, transactions, stats = census(blocks, protocol['blocks'])
    check_case_anchors(records,loaded['source_view']['rows'],transactions)
    chosen, strata = choose(first,excluded,protocol['comparison_selection']['quotas'],
                            protocol['comparison_selection']['hash_prefix'])
    rows = [dict(source_id=f'comparison_{i:04d}',address_sha256=digest(r['address'].encode()),
                 payment_txid_sha256=digest(r['reference_txid'].encode()),
                 cutoff_height=r['cutoff_height'],cutoff_block_hash=r['cutoff_block_hash'],
                 known_coldcard_core_membership=0,compromise_label=None,hardware_label=None,
                 features=None,history_status='pending') for i,r in enumerate(chosen,1)]
    result = dict(schema_version=1,protocol_sha256=digest(path.read_bytes()),snapshots=snapshots,
                census=stats,strata=strata,case_sources_reconciled=len(records),rows=rows,
                source_address_count_before_exclusions=len(first),selected_comparison_sources=len(rows),
                unknown_is_legitimate=False,history_collection_performed=False,training_performed=False)
    if not include_census:
        return result
    public = [dict(address_sha256=digest(address.encode()),
                   payment_txid_sha256=digest(row['reference_txid'].encode()),
                   cutoff_height=row['cutoff_height'],cutoff_block_hash=row['cutoff_block_hash'],
                   selection_key=digest((protocol['comparison_selection']['hash_prefix']+address).encode()),
                   excluded_known_related=address in excluded) for address,row in first.items()]
    public.sort(key=lambda r:r['address_sha256'])
    if len({r['selection_key'] for r in public})!=len(public):
        raise ValueError('Hash tie requires explicit raw-address tie audit')
    normalized = dict(schema_version=1,protocol_sha256=result['protocol_sha256'],
                      basis={k:v for k,v in result.items() if k!='rows'},sources=public,
                      limitation='Redacted provider-derived census reproduces selection; it is not independent block inclusion or owner/device verification.')
    return result, normalized


def replay(path, census_file):
    protocol, _, _, excluded = load_design(path)
    normalized=json.loads(gzip.decompress(census_file.read_bytes()))
    if normalized['protocol_sha256']!=digest(path.read_bytes()):
        raise ValueError('Redacted census protocol mismatch')
    public=normalized['sources']
    if len({r['address_sha256'] for r in public})!=len(public) or len({r['selection_key'] for r in public})!=len(public):
        raise ValueError('Duplicate redacted source/key')
    excluded_hashes={digest(a.encode()) for a in excluded}
    for r in public:
        if r['excluded_known_related'] != (r['address_sha256'] in excluded_hashes):
            raise ValueError('Redacted exclusion flag mismatch')
    result=dict(normalized['basis'])
    selected,strata=[],[]
    for quota in protocol['comparison_selection']['quotas']:
        pool=sorted((r for r in public if not r['excluded_known_related'] and r['cutoff_height']==quota['height']),
                    key=lambda r:r['selection_key'])
        take=pool[:quota['comparison_quota']]
        selected.extend(take)
        strata.append(dict(height=quota['height'],eligible_sources=len(pool),quota=quota['comparison_quota'],
                           selected_sources=len(take),shortfall=max(0,quota['comparison_quota']-len(take))))
    result['rows']=[dict(source_id=f'comparison_{i:04d}',
                        **{k:r[k] for k in ('address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash')},
                        known_coldcard_core_membership=0,compromise_label=None,hardware_label=None,
                        features=None,history_status='pending') for i,r in enumerate(selected,1)]
    result.update(strata=strata,source_address_count_before_exclusions=len(public),selected_comparison_sources=len(selected))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('audit','select','verify','census','replay'))
    parser.add_argument('protocol',type=Path)
    parser.add_argument('cache',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    if args.command=='audit':result=audit(args.protocol,args.cache)
    elif args.command=='census':_,result=select(args.protocol,args.cache,include_census=True)
    elif args.command=='replay':result=replay(args.protocol,args.cache)
    else:result=select(args.protocol,args.cache)
    raw=json_bytes(result)
    if args.command=='census':raw=gzip.compress(raw,mtime=0)
    if args.command in ('verify','replay'):
        if args.output.read_bytes()!=raw:raise ValueError('Selection reproduction mismatch')
    else:
        with args.output.open('xb') as stream:stream.write(raw)
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','sources','basis')},indent=2))


if __name__=='__main__':main()
