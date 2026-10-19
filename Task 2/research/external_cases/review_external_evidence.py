"""Reconcile published theft evidence and official donation comparison candidates."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request
import pandas as pd

CONTROLS = [
    ('internet_archive', '1Archive1n2C579dMsAu3iC6tWzuQJz8dN', 'https://archive.org/donate/cryptocurrency'),
    ('eff', '3LTu6uavQ4A3kgDauZipyGqcHQEUSVe2so', 'https://www.eff.org/pages/other-ways-give-and-donor-support'),
    ('fsf', '1PC9aZC4hNX2rmmrt7uHTfYAS3hRbph4UN', 'https://www.fsf.org/about/ways-to-donate'),
]
COLLECTOR_A = '19jSfadPiKa4aCefj4F7uEYbhMEt2L8SCH'
COLLECTOR_B = '17C7EZC1VTrXzSQneiaJv2W6tQh1vCRSnF'
OPERATOR_TX = '10f219c427635e50dc374af6aa601e6f412ac0dccc7c545932afba5f818808f0'


def fetch(url):
    with urllib.request.urlopen(url, timeout=20) as response:
        return response.read()


def control(item):
    name, address, url = item
    record = dict(entity_group=name, address=address, source_url=url,
                  role='officially_published_donation_recipient', training_label='pending_comparison_policy',
                  label_available_at=None, history_complete=False)
    try:
        page = fetch(url)
        record.update(page_sha256=hashlib.sha256(page).hexdigest(), address_found_in_official_html=address.encode() in page)
    except Exception as error:
        record['page_fetch_error'] = str(error)
    try:
        payload = fetch('https://blockstream.info/api/address/' + address)
        record.update(provider='https://blockstream.info/api', provider_response_sha256=hashlib.sha256(payload).hexdigest(),
                      provider_counters=json.loads(payload))
    except Exception as error:
        record['provider_error'] = str(error)
    return record


def run(histories, source, output):
    if output.exists():
        raise ValueError('Output must be new')
    a = json.loads((histories / (COLLECTOR_A + '.json')).read_text())
    b = json.loads((histories / (COLLECTOR_B + '.json')).read_text())
    tx = next(t for t in a['transactions'] if t['txid'] == OPERATOR_TX)
    facts = dict(txid=tx['txid'], input_count=len(tx['vin']), output_count=len(tx['vout']),
                 input_sat=sum(v['prevout']['value'] for v in tx['vin']),
                 outputs=[dict(address=v.get('scriptpubkey_address'), value_sat=v['value']) for v in tx['vout']],
                 fee_sat=tx['fee'], status=tx['status'])
    assert facts['input_count'] == 4 and facts['output_count'] == 1
    assert facts['input_sat'] == 578705 and facts['fee_sat'] == 1928
    assert facts['outputs'] == [dict(address=COLLECTOR_A, value_sat=576777)]
    links = []
    incoming_a = [t for t in a['transactions'] if any(v.get('scriptpubkey_address') == COLLECTOR_A for v in t['vout'])]
    incoming_b = [t for t in b['transactions'] if any(v.get('scriptpubkey_address') == COLLECTOR_B for v in t['vout'])]
    for first in incoming_b:
        for second in incoming_a:
            for vin in second['vin']:
                if vin['txid'] == first['txid']:
                    links.append(dict(parent_txid=first['txid'], parent_output=vin['vout'], child_txid=second['txid'], value_sat=vin['prevout']['value']))
    with ThreadPoolExecutor(max_workers=3) as pool:
        controls = list(pool.map(control, CONTROLS))
    bb = set(pd.read_csv(source / 'BB.tsv', sep='\t', usecols=['address']).address)
    cb = set(pd.read_csv(source / 'CB.tsv', sep='\t', usecols=['address']).address)
    for record in controls:
        record['real_cats_overlap'] = dict(BB=record['address'] in bb, CB=record['address'] in cb)
    report = dict(reviewed_at=datetime.now(timezone.utc).isoformat(), status='Evidence-reviewed pilot; not a labeled evaluation dataset',
                  operator_report_url='https://cafe.tollbooth-dpyc.com/blogs/our-value/anatomy-of-a-lightning-theft-no-balances-lost',
                  operator_transaction_reconciliation=facts, saved_history_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [histories/(COLLECTOR_A+'.json'),histories/(COLLECTOR_B+'.json')]},
                  collector_A_evidence='Direct operator theft testimony; transaction facts agree with saved provider observations; testimony is not independently authenticated',
                  collector_B_evidence='Research attribution with reconciled transaction dependency; no direct operator testimony found for B',
                  cross_collector_transaction_dependencies=links,
                  dependency_interpretation='An output of a transaction paying B is later consumed by a transaction paying A; this alone does not prove both destination private keys share an owner',
                  controls=controls, limitations=['Official donation purpose is supported; incoming fund legitimacy is not established',
                  'Three entities are a convenience comparison pilot, not representative benign ground truth',
                  'Provider counters are current observations, not full historical features',
                  'Source labels are retrospective; no model fitting or predictions performed'])
    output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(operator_transaction=facts, links=links, controls=controls),indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('histories',type=Path)
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    run(args.histories,args.source,args.output)
