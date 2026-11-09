"""New 32-page coverage scope; reuse the validated collector and original route."""
import argparse
from contextlib import ExitStack
from datetime import datetime,timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re
import sys


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok,message):
    if not ok:raise ValueError(message)


def main(protocol_path,output,work):
    protocol=json.loads(protocol_path.read_bytes());output.mkdir(parents=True,exist_ok=True)
    require(not (output/'run_receipt.json').exists(),'Stopped scope cannot be rerun')
    lock_file=work/'historical_locks.json'
    require(digest(lock_file)==protocol['private_lock_manifest_sha256'],'Lock manifest changed')
    sys.path.insert(0,str(protocol_path.parent.parent))
    import collect_reference_tail as tail
    import collect_reference_tail_many as many
    from comparison_http import PersistentHTTP
    original_guarded=tail.guarded
    def stop_before_new_source(record,pages,work,max_pages):
        if pages.stop.is_set():raise InterruptedError('Stopped before a new source start')
        return original_guarded(record,pages,work,max_pages)
    tail.guarded=stop_before_new_source
    class LeasedHTTP(PersistentHTTP):
        def __enter__(self):
            permit=json.loads((work/'lease_published').read_bytes())
            lease=permit['collector_lease'];now=datetime.now(timezone.utc)
            require(lease['state']=='running' and lease['owner']==protocol['pass_name'],'Foreign or idle lease')
            require(lease['protocol_sha256']==digest(protocol_path),'Published protocol differs')
            require(datetime.fromisoformat(lease['expires_at'])>now,'Published lease expired')
            due=permit.get('next_network_attempt_not_before')
            require(not due or datetime.fromisoformat(due)<=now,'Network cooldown is not due')
            require(len(permit['published_commit'])==40,'Published lease not verified')
            return super().__enter__()
    tail.PersistentHTTP=LeasedHTTP
    with ExitStack() as stack:
        for path in json.loads(lock_file.read_bytes()):
            lock=stack.enter_context(Path(path).open('a+'))
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                (output/'run_receipt.json').write_text(json.dumps(dict(status='local_lock_held_no_http',provider_requests=0,model_fits=0))+'\n')
                print('LOCAL_LOCK_HELD_NO_HTTP',flush=True);return
        # tail.run acquires the new work lock, announces readiness, and waits
        # for a permit written only after GitHub lease publication/readback.
        many.main(protocol_path,output,work)
    metadata=[json.loads(p.read_bytes()) for p in sorted((work/'requests').glob('*/*.json'))]
    new=[m for m in metadata if not m.get('offline_reused')]
    def status(m):
        if m.get('http_status'):return m['http_status']
        found=re.search(r'Tunnel connection failed:\s*(403|429)',m.get('reason',''))
        return int(found.group(1)) if found else None
    denied=sorted([m for m in new if status(m) in (403,429)],key=lambda m:m.get('finished_at',m['started_at']))
    first=denied[0] if denied else None
    receipt=dict(schema_version=1,pass_name=protocol['pass_name'],status='stopped_refusal' if first else 'bounded_run_finished',
        new_request_records=len(new),new_http_200=sum(status(m)==200 for m in new),
        offline_responses_reused=sum(bool(m.get('offline_reused')) for m in metadata),
        first_refusal_status=status(first) if first else None,retry_after=first.get('retry_after') if first else None,
        refusal_at=first.get('finished_at') if first else None,model_fits=0,automatic_retry_performed=False,
        provider_or_route_changed=False,operational_locks_released=True,
        full_current_history_statuses_promoted=False)
    (output/'run_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('SCOPE_RECEIPT '+json.dumps(receipt,sort_keys=True),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol',type=Path);parser.add_argument('output',type=Path);parser.add_argument('work',type=Path)
    a=parser.parse_args();main(a.protocol.resolve(),a.output.resolve(),a.work.resolve())
