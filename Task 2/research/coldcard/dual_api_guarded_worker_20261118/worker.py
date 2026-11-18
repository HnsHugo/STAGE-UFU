"""One in-process native collector, with durable lifecycle identity before HTTP."""
import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from prepare_frontier_checkpoint import read, write, sha
from dual_api_frontier import exclusive_run


def guarded(call, work, scope, commit):
    path = work / 'worker_lifecycle.json'
    if path.exists():
        raise ValueError('Consumed worker lifecycle; fresh scope required')
    stat = Path('/proc/self/stat').read_text().rsplit(') ', 1)[1].split()
    identity = dict(scope=scope, published_commit=commit, pid=os.getpid(),
                    process_start_ticks=stat[19],
                    boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                    pid_namespace=os.readlink('/proc/self/ns/pid'),
                    mount_namespace=os.readlink('/proc/self/ns/mnt'),
                    phase='running', started_at=datetime.now(timezone.utc).isoformat())
    write(path, identity)
    error = None
    try:
        return call()
    except BaseException as exc:
        error = type(exc).__name__
        raise
    finally:
        identity.update(phase='finished', error_type=error,
                        finished_at=datetime.now(timezone.utc).isoformat())
        receipt = work.parent / scope / 'run_receipt.json'
        if receipt.exists():
            identity['run_receipt_sha256'] = sha(receipt)
        write(path, identity)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'run'])
    parser.add_argument('scope')
    parser.add_argument('parent')
    parser.add_argument('source')
    parser.add_argument('commit', nargs='?')
    args = parser.parse_args()
    for value in [args.scope, args.parent, args.source]:
        if '/' in value or value in ['.', '..']:
            raise ValueError('Invalid scope identifier')
    import dual_api_native_unit as native
    native.SCOPE, native.PARENT, native.SID = args.scope, args.parent, args.source
    native.OUT = BASE / args.scope
    native.WORK = BASE / ('source_cohort_work_' + args.scope)
    worker_key = str(Path(__file__).resolve().relative_to(BASE))
    if args.command == 'prepare':
        result = native.prepare()
        with exclusive_run(read(native.WORK / 'historical_locks.json')):
            policy = read(native.POLICY)
            assert policy['collector_lease'] == read(native.OUT / 'authorization.json')['collector_lease']
            assert policy['collector_lease']['owner'] == args.scope
            protocol = read(native.OUT / 'protocol.json')
            protocol['code_pins'][worker_key] = sha(Path(__file__))
            protocol['worker_lifecycle'] = 'Same in-process collector; identity saved before run; final receipt on normal/exceptional exit'
            write(native.OUT / 'protocol.json', protocol)
            policy['collector_lease']['protocol_sha256'] = sha(native.OUT / 'protocol.json')
            write(native.POLICY, policy)
            write(native.OUT / 'authorization.json', dict(collector_lease=policy['collector_lease']))
        return result
    protocol = read(native.OUT / 'protocol.json')
    assert protocol['code_pins'][worker_key] == sha(Path(__file__))
    return guarded(lambda: native.run(args.commit), native.WORK, args.scope, args.commit)


if __name__ == '__main__':
    import json
    print(json.dumps(main()))
