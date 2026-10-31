"""Apply the validated reference-tail method with a verified export per batch."""
import argparse
import contextlib
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import sys

from build_source_registry import digest, json_bytes
import collect_reference_tail as tail
import prepayment_pilot as fixed
from source_cohort import atomic_write


def verify(q, output, work):
    proto = json.loads(q.read_bytes())
    cp = json.loads(gzip.decompress((output/'checkpoint.json.gz').read_bytes()))
    if cp['protocol_sha256'] != digest(q.read_bytes()):
        raise ValueError('Export protocol fingerprint mismatch')
    if not set(cp['entries']) <= set(proto['source_ids']):
        raise ValueError('Export contains an unselected source')
    for key, entry in cp['entries'].items():
        if key != entry['source_id']:
            raise ValueError('Export source key mismatch')
        if digest((work/entry['raw_file']).read_bytes()) != entry['raw_sha256']:
            raise ValueError('Export raw fingerprint mismatch')
        if entry['status'] == 'complete_prior_prefix':
            if fixed.features(entry['prefix'],entry['cutoff_height']) != entry['features']:
                raise ValueError('Export feature vector differs from normalized evidence')
        elif entry['status'] != 'bounded_incomplete' or entry['features'] is not None:
            raise ValueError('Invalid unavailable prefix result')
    return len(cp['entries'])


class Journal:
    def __init__(self, stream, q, output, work):
        self.stream, self.q, self.output, self.work = stream, q, output, work
        self.buffer = ''

    def write(self, value):
        self.stream.write(value)
        self.buffer += value
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n',1)
            if line.startswith('BATCH '):
                count = verify(self.q,self.output,self.work)
                self.stream.write('EXPORT_VERIFIED '+str(count)+'\n')
            if line.startswith('STOPPED '):
                atomic_write(self.output/'collection_stop.json',json_bytes(dict(
                    stopped_at=datetime.now(timezone.utc).isoformat(), reason=line[8:],
                    automatic_retry_performed=False, provider_or_route_changed=False)))

    def flush(self):
        self.stream.flush()


def main(q,output,work):
    proto = json.loads(q.read_bytes())
    gate = json.loads((q.parent/proto['inputs']['pilot_validation']['file']).read_bytes())
    if gate.get('all_exact_matches') is not True or gate.get('pilot_controls') != 8:
        raise ValueError('The eight-control exact-match gate is not satisfied')
    with contextlib.redirect_stdout(Journal(sys.stdout,q,output,work)):
        tail.run(q,output,work)
    verify(q,output,work)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('work',type=Path)
    args=parser.parse_args()
    main(args.protocol,args.output,args.work)
