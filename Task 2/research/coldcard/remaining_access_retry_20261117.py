import remaining_access_checkpoint as a
import argparse,json
from prepare_frontier_checkpoint import read,sha,write
from pathlib import Path
a.OUT=a.BASE/'mempool_remaining_fifty_20261116_access_retry_20261117'
a.WORK=a.BASE/('source_cohort_work_'+a.OUT.name)
p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','authorize','run','finish']);command=p.parse_args().command
r=getattr(a,command)()
if command=='prepare':
 q=read(a.OUT/'protocol.json');q['baseline_vectors']=1457;q['inputs']['retry_driver']=dict(file='../'+Path(__file__).name,sha256=sha(Path(__file__)));write(a.OUT/'protocol.json',q)
if r is not None:print(json.dumps(r))
