"""Record collector receipt structure and reference overlap without unknown IDs."""
import argparse
import json
from pathlib import Path
from rank_block_recipients import digest, load_references, load_protocol, validate_block, verify_history_receipts


def diagnose(protocol_path, summary_path, cache, original_path):
    protocol=load_protocol(protocol_path);summary=json.loads(summary_path.read_text())
    if digest(protocol_path.read_bytes())!=summary['protocol_sha256']:
        raise ValueError('Protocol checksum mismatch')
    histories=load_references(protocol,protocol_path.parent)
    pinned={b['height']:b for b in summary['blocks']};blocks=[]
    for entry in protocol['blocks']:
        raw=(cache/(str(entry['height'])+'.json')).read_bytes()
        if digest(raw)!=pinned[entry['height']]['raw_json_sha256']:
            raise ValueError('Block checksum mismatch')
        b=json.loads(raw);validate_block(b,entry);blocks.append(b)
    records=[]
    for i,ref in enumerate(protocol['references']):
        address=ref['address'];transactions=[]
        for block in blocks:
            verify_history_receipts(block,histories[address])
            for tx in block['tx']:
                if not any(o.get('addr')==address and o['value']>0 for o in tx['out']):continue
                transactions.append(dict(height=block['height'],input_count=len(tx['inputs']),
                    output_count=len(tx['out']),output_values_sat=[o['value'] for o in tx['out']],
                    receipt_value_sat=sum(o['value'] for o in tx['out'] if o.get('addr')==address)))
        records.append(dict(reference_id='reference_'+str(i+1),receipts=transactions))
    original=json.loads(original_path.read_text())
    return dict(protocol_sha256=digest(protocol_path.read_bytes()),receipts=records,
                reference_address_overlap_with_central=len({r['address'] for r in protocol['references']}&
                    {r['address'] for r in original['references']}),
                limits=['Only exact reference-address overlap is checked, not entity independence',
                        'Provider receipt agreement is not cryptographic block inclusion proof',
                        'Second-output role remains unknown; no output is removed to improve ranking',
                        'This is a separate software-incident diagnostic, not hardware-device ground truth'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('protocol','summary','cache','central_protocol','output'):p.add_argument(name,type=Path)
    a=p.parse_args();r=diagnose(a.protocol,a.summary,a.cache,a.central_protocol)
    with a.output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
