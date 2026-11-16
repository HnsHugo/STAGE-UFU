"""Read an omitted legacy provider field from its pinned acquisition protocol.

This preparation-only adapter leaves old code and cached marker bytes intact.
It neither sends a request nor relaxes body, endpoint, identity or overlap checks.
"""
import argparse
from datetime import datetime,timezone
from pathlib import Path

import recorded_twenty_campaign as campaign
from prepare_frontier_checkpoint import read,write,sha


def provider_metadata(meta, protocol):
    expected=protocol['provider']
    if expected!='https://blockstream.info/api':
        raise ValueError('Unexpected provider in the legacy acquisition protocol')
    if 'provider' in meta and meta['provider']!=expected:
        raise ValueError('Legacy marker conflicts with its acquisition protocol')
    return dict(meta,provider=expected)


def prepare(number):
    selection=read(campaign.CAMPAIGN/'selection.json')
    unit=selection['units'][number-1]
    assert unit['kind']=='legacy_bridge'
    tests=campaign.CAMPAIGN/'compatibility_tests_20261116.json'
    assert read(tests)['status']=='passed'
    original=campaign.read
    inferred=set();protocols={}
    def compatible(path):
        value=original(path);path=Path(path).resolve()
        if path.suffix=='.json' and path.parent.parent.name=='requests' and path.parents[2].name=='source_cohort_work_source_prefix_extension_20261112_02':
            assert path.parent.name in unit['source_ids'] and value['source_id']==path.parent.name
            protocol_path=campaign.BASE/'source_prefix_extension_20261112_02/protocol.json'
            source=original(protocol_path)
            protocols[protocol_path]=sha(protocol_path)
            if 'provider' not in value:inferred.add((value['source_id'],value['key']))
            return provider_metadata(value,source)
        return value
    campaign.read=compatible
    try:result=campaign.prepare(number)
    finally:campaign.read=original
    out=campaign.BASE/result['scope'];q=read(out/'protocol.json')
    proof=dict(status='passed',inferred_marker_fields=len(inferred),source_ids=unit['source_ids'],
        rule='A missing provider tag is read from the fingerprint-pinned original acquisition protocol. Explicit conflicts are rejected. Original marker/body bytes remain unchanged.',
        source_protocols=[dict(file=str(p.relative_to(campaign.BASE)),sha256=h) for p,h in protocols.items()],
        new_provider_requests_during_preparation=0)
    write(out/'legacy_provider_provenance.json',proof)
    for key,path in [('legacy_metadata_adapter',Path(__file__).resolve()),('legacy_provider_provenance',out/'legacy_provider_provenance.json'),('legacy_compatibility_tests',tests)]:
        import os
        q['inputs'][key]=dict(file=os.path.relpath(path,out),sha256=sha(path))
    q['legacy_provider_field_inference']='Original pinned Blockstream protocol; no cached file rewritten'
    q['prepared_at']=datetime.now(timezone.utc).isoformat()
    write(out/'protocol.json',q)
    verification=read(out/'preparation_verification.json');verification.update(input_pins_verified=len(q['inputs']),legacy_provider_field_compatibility='passed',cached_files_rewritten=0)
    write(out/'preparation_verification.json',verification)
    return dict(result,legacy_provider_fields_inferred=len(inferred))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare']);p.add_argument('number',type=int);a=p.parse_args()
    print(__import__('json').dumps(prepare(a.number),sort_keys=True))
