"""Import source assertions as candidates, without promoting them to ground truth."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def read(path,delimiter):
    with path.open() as f:return list(csv.DictReader(f,delimiter=delimiter))


def run(source,output):
    manifest=json.loads((source/'download_manifest.json').read_text())
    for entry in manifest:
        path=source/entry['repo'].split('/')[1]/entry['path']
        if len(path.read_bytes())!=entry['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('Source checksum mismatch')
    records=[]
    for row in read(source/'coldcard-drain-addresses/attacker-addresses.csv',','):
        records.append(dict(address=row['address'],source_id='coldcard_research',
            asserted_role=row['role'],wave=row['wave'],conservative_split_group='coldcard_2026_all_waves',
            evidence='source_onchain_reconstruction_not_independent_theft_confirmation',training_label='pending_review'))
    for row in read(source/'btcpay-lnd-drain-2026-08/collectors.csv',','):
        records.append(dict(address=row['address'],source_id='btcpay_research',asserted_role='collector',
            conservative_split_group='btcpay_lnd_20260807',evidence='research_report_with_described_victim_testimony',training_label='pending_review'))
    criminal=read(source/'Real-CATS/CB.tsv','\t')
    selected=[r for r in criminal if r['label'] in {'Hack','Theft'} and float(r['transaction_number'])>0]
    for row in selected:
        records.append(dict(address=row['address'],source_id='real_cats',source_label=row['label'],
            role='unknown',case_id=None,label_available_at=None,training_label='pending_provenance_review'))
    benign=[r for r in read(source/'Real-CATS/BB.tsv','\t') if float(r['transaction_number'])>0]
    # Deterministic pilot selection; based on address hash, not financial feature values.
    benign=sorted(benign,key=lambda r:hashlib.sha256(r['address'].encode()).hexdigest())[:50]
    for row in benign:
        records.append(dict(address=row['address'],source_id='real_cats',source_label='benign',role='unknown',
            case_id=None,label_available_at=None,selection='first_50_active_addresses_by_sha256',training_label='pending_comparison_policy_review'))
    report=dict(status='candidate_registry_not_supervised_dataset',sources=manifest,records=records,
                victim_lists_imported=False,case_split_ready=False,
                warning='Source classes/roles are assertions; no model training labels assigned automatically')
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print('Candidate assertions:',len(records))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();run(a.source,a.output)
