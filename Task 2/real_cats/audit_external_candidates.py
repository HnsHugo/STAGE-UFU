"""Audit registry independence without evaluating or predicting any address."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
import pandas as pd
from train_source_categories import HASHES, prepare, split


def run(source, registry, output):
    for name, expected in HASHES.items():
        with (source / name).open('rb') as handle:
            if hashlib.file_digest(handle, 'sha256').hexdigest() != expected:
                raise ValueError('Source checksum mismatch')
    bb = pd.read_csv(source / 'BB.tsv', sep='\t')
    cb = pd.read_csv(source / 'CB.tsv', sep='\t')
    data = prepare(bb, cb)
    train, val, test = split(data)
    membership = {data.iloc[i].address: name for name, indices in [('train', train), ('validation', val), ('reserved_test', test)] for i in indices}
    all_source = set(bb.address) | set(cb.address)
    records = json.loads(registry.read_text())['records']
    sources = {}
    for source_id in sorted({r['source_id'] for r in records}):
        subset = [r for r in records if r['source_id'] == source_id]
        addresses = {r['address'] for r in subset}
        sources[source_id] = dict(assertions=len(subset), unique_addresses=len(addresses),
            split_overlap=dict(Counter(membership[a] for a in addresses if a in membership)),
            overlap_any_real_cats=int(len(addresses & all_source)),
            absent_from_real_cats=int(len(addresses - all_source)),
            training_label_counts=dict(Counter(r['training_label'] for r in subset)),
            known_split_groups=sorted({r['conservative_split_group'] for r in subset if r.get('conservative_split_group')}))
    report = dict(status='No independent labeled evaluation set established',
                  registry_sha256=hashlib.sha256(registry.read_bytes()).hexdigest(), source_sha256=HASHES,
                  sources=sources, operation='Address membership audit only; no test features or predictions',
                  cautions=['Address non-overlap does not prove incident/entity independence',
                            'Pending-review assertions cannot establish positive or negative ground truth',
                            'External histories need an explicitly compatible feature extraction schema'])
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('registry', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    run(args.source, args.registry, args.output)
