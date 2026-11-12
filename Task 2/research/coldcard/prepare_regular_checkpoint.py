"""Prepare a regular deeper checkpoint and refresh inherited resume metadata."""
import argparse
import json
from pathlib import Path
from prepare_coldcard_checkpoint import prepare, read, sha, json_bytes


def prepare_regular(parent, output, maximum):
    result = prepare(parent, output, maximum)
    output = output.resolve()
    protocol = read(output / 'protocol.json')
    protocol['per_source_saved_pages'] = {sid:protocol['previous_bound'] for sid in protocol['source_ids']}
    protocol['previous_requested_page_target'] = protocol['previous_bound']
    protocol['finalization_entrypoint'] = protocol['inputs']['finalization_code']['file']
    if 'network_not_before' in protocol:
        protocol['network_entrypoint'] = '../run_after_cooldown.py'
    protocol['inputs']['regular_metadata_code'] = dict(file='../'+Path(__file__).name,sha256=sha(Path(__file__)))
    (output/'protocol.json').write_bytes(json_bytes(protocol))
    resume = read(output/'resume_checkpoint.json')
    resume['protocol_sha256'] = sha(output/'protocol.json')
    (output/'resume_checkpoint.json').write_bytes(json_bytes(resume))
    for pin in protocol['inputs'].values():
        assert sha((output/pin['file']).resolve()) == pin['sha256']
    verification = read(output/'preparation_verification.json')
    verification.update(protocol_sha256=resume['protocol_sha256'],
        input_pins_verified=len(protocol['inputs']),regular_resume_metadata_refreshed=True)
    (output/'preparation_verification.json').write_bytes(json_bytes(verification))
    return dict(verification,request_budget=result['request_budget'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parent',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('maximum',type=int)
    args = parser.parse_args()
    print(json.dumps(prepare_regular(args.parent,args.output,args.maximum),sort_keys=True))
