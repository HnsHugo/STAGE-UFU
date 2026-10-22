"""Extend the central ranking by exactly one neighboring block on each side."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import urllib.request
from rank_block_recipients import analyze, digest, validate_block


def check_selection(selection, original):
    expected = set()
    for group in {b['case_group'] for b in original['blocks']}:
        blocks = sorted((b for b in original['blocks'] if b['case_group']==group), key=lambda b:b['height'])
        for side, boundary, offset in [('before',blocks[0],-1),('after',blocks[-1],1)]:
            expected.add((group,boundary['height']+offset,boundary['height'],side))
    actual = [(n['case_group'],n['height'],n['boundary_height'],n['side']) for n in selection['neighbors']]
    if len(actual)!=len(expected) or set(actual)!=expected:
        raise ValueError('Exactly one adjacent block on each side of each incident is required')


def check_link(neighbor, boundary, side):
    if side=='before':
        valid = boundary['prev_block']==neighbor['hash'] and neighbor['height']+1==boundary['height']
    else:
        valid = neighbor['prev_block']==boundary['hash'] and neighbor['height']==boundary['height']+1
    if not valid:
        raise ValueError('Neighbor does not link to the selected incident boundary')


def run(selection_path, cache, protocol_path, output):
    selection = json.loads(selection_path.read_text())
    base = selection_path.parent/selection['base_protocol']
    original = json.loads(base.read_text())
    check_selection(selection,original)
    if protocol_path.exists() or output.exists():
        raise ValueError('New protocol and result paths required')
    cache.mkdir(parents=True,exist_ok=True)
    def fetch(entry):
        path = cache/(str(entry['height'])+'.json')
        if path.exists():
            raw = path.read_bytes()
        else:
            url = 'https://blockchain.info/rawblock/'+entry['hash']+'?format=json'
            with urllib.request.urlopen(url,timeout=40) as response: raw=response.read()
        block = json.loads(raw)
        anchor = {k:entry[k] for k in ('case_group','height','hash')}
        anchor['time'] = block['time']
        validate_block(block,anchor)
        boundary = json.loads((cache/(str(entry['boundary_height'])+'.json')).read_bytes())
        boundary_anchor = next(b for b in original['blocks'] if b['height']==entry['boundary_height'])
        validate_block(boundary,boundary_anchor)
        check_link(block,boundary,entry['side'])
        if not path.exists():
            with path.open('xb') as stream: stream.write(raw)
        return anchor
    with ThreadPoolExecutor(max_workers=4) as executor:
        neighbors = list(executor.map(fetch,selection['neighbors']))
    protocol = dict(original)
    protocol.update(scope=selection['scope'],selection=selection['selection_rule'],
                    selection_manifest_sha256=digest(selection_path.read_bytes()),
                    base_protocol_sha256=digest(base.read_bytes()),
                    created_before_full_block_ranking=False,
                    note='Baseline results already known; neighboring window fixed before its acquisition and ranking')
    protocol['blocks'] = sorted(original['blocks']+neighbors,key=lambda b:b['height'])
    # Reference-history paths stay relative to the existing research directory.
    if protocol_path.parent.resolve()!=selection_path.parent.resolve():
        raise ValueError('Protocol must share the reference-history base directory')
    with protocol_path.open('x') as stream: json.dump(protocol,stream,indent=2);stream.write('\n')
    return analyze(protocol_path,cache,output)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('selection',type=Path);p.add_argument('cache',type=Path)
    p.add_argument('protocol',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args()
    result=run(a.selection,a.cache,a.protocol,a.output)
    print(json.dumps({'transaction_count':result['transaction_count'], 'case_groups':len(result['cohorts'])}))
