"""Describe fixed top-10 collection-pattern candidates, without assigning labels."""
import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import median
from rank_block_recipients import (FEATURES, add_rows, coinbase, digest,
                                   rank_interval, recipient_features, validate_block)

SCORE = FEATURES[1]


def select_candidates(rows, budget=10):
    """Include every tie at the review boundary; never choose by address order."""
    if budget < 1:
        raise ValueError('Positive review budget required')
    if not rows:
        return []
    cutoff = sorted((r[SCORE] for r in rows.values()),reverse=True)[min(budget,len(rows))-1]
    return [a for a in rows if rows[a][SCORE] >= cutoff]


def describe(address, blocks):
    receipts, sources, qualifying_sources, values, counts = [], set(), set(), [], Counter()
    single, external, self_input, unknown, multi_input = 0, 0, 0, 0, 0
    scripts = set()
    for block in blocks:
        for tx in block['tx']:
            if coinbase(tx):
                continue
            outputs = [o for o in tx['out'] if o.get('addr')==address and o['value']>0]
            if not outputs:
                continue
            receipts.append(tx['hash']); counts[str(block['height'])] += 1
            values.append(sum(o['value'] for o in outputs))
            scripts.update(o.get('script','') for o in outputs)
            inputs = [(i.get('prev_out') or {}).get('addr') for i in tx['inputs']]
            sources.update(a for a in inputs if a is not None)
            self_input += address in inputs
            unknown += any(a is None for a in inputs)
            multi_input += len(inputs)>1
            if len(tx['out'])==1:
                single += 1
                if inputs and all(a not in (None,address) for a in inputs):
                    external += 1; qualifying_sources.update(inputs)
    if not receipts:
        raise ValueError('Profile requires an observed recipient')
    return dict(receipt_transactions=len(receipts),single_output_transactions=single,
                external_single_output_transactions=external,
                external_single_output_fraction=external/len(receipts),
                receipts_with_self_input=self_input,receipts_with_unknown_input=unknown,
                receipts_with_multiple_inputs=multi_input,
                distinct_decoded_input_addresses=len(sources),
                distinct_qualifying_input_addresses=len(qualifying_sources),
                receipt_value_sat=dict(min=min(values),median=median(values),max=max(values),total=sum(values)),
                receipt_counts_by_height=dict(sorted(counts.items())),
                has_p2a_anchor_output='51024e73' in scripts)


def run(protocol_path, summary_path, cache):
    protocol=json.loads(protocol_path.read_text()); saved=json.loads(summary_path.read_text())
    if saved['protocol_sha256'] != digest(protocol_path.read_bytes()):
        raise ValueError('Protocol checksum mismatch')
    pinned={b['height']:b for b in saved['blocks']}
    groups={}; rows={}
    for entry in protocol['blocks']:
        raw=(cache/(str(entry['height'])+'.json')).read_bytes()
        if digest(raw)!=pinned[entry['height']]['raw_json_sha256']:
            raise ValueError('Raw-block checksum differs from saved experiment')
        block=json.loads(raw);validate_block(block,entry)
        group=entry['case_group'];groups.setdefault(group,[]).append(block)
        add_rows(rows.setdefault(group,{}),recipient_features(block['tx']))
    refs={r['address']:'reference_'+str(i+1) for i,r in enumerate(protocol['references'])}
    results=[]
    for group, population in sorted(rows.items()):
        expected=next(r for r in saved['pooled_results'] if r['case_group']==group)
        if len(population)!=expected['recipient_count']:
            raise ValueError('Recipient population differs from saved ranking')
        selected=select_candidates(population)
        # Address sorting only assigns stable anonymous IDs; rank intervals are unchanged.
        selected.sort(key=lambda a:(-population[a][SCORE],a))
        profiles=[]
        for i,address in enumerate(selected):
            metrics=describe(address,groups[group]); rank=rank_interval(population,address,SCORE)
            if metrics['external_single_output_transactions']!=rank['score']:
                raise ValueError('Profile does not reproduce the fixed baseline score')
            profiles.append(dict(candidate_id='candidate_'+str(i+1),reference_id=refs.get(address),
                                 rank=rank,**metrics))
        leader=max(population,key=lambda a:population[a][FEATURES[0]])
        leader_metrics=describe(leader,groups[group])
        results.append(dict(case_group=group,recipient_count=len(population),
                            review_budget=10,selected_with_boundary_ties=len(profiles),profiles=profiles,
                            receipt_count_leader=dict(reference_id=refs.get(leader),
                                collection_rank=rank_interval(population,leader,SCORE),**leader_metrics)))
    return dict(protocol_sha256=digest(protocol_path.read_bytes()),
                ranking_summary_sha256=digest(summary_path.read_bytes()),groups=results,
                scope='Descriptive profiles of all fixed top-10 ranks including boundary ties; no labels assigned',
                limits=['Anonymous IDs are local to each case, not entities or ownership clusters',
                        'Input addresses count decoded strings, not victims, people or hardware devices',
                        'Unknown recipients are neither confirmed false positives nor confirmed criminals',
                        'Input amounts, future spending and external identity labels are not used',
                        'Repeated receipts within the same incident are not independent incidents'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('protocol','summary','cache','output'): p.add_argument(name,type=Path)
    a=p.parse_args(); report=run(a.protocol,a.summary,a.cache)
    with a.output.open('x') as f: json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'groups':len(report['groups']),'profiles':sum(len(g['profiles']) for g in report['groups'])}))
