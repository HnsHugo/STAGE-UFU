"""Archive a verified private evidence layer, excluding operational flags.

Public code and exports remain in Git. The archive contains only the private
working evidence and its per-file manifest; saving it is a separate operation.
"""
import argparse
from contextlib import ExitStack
import fcntl
import hashlib
import io
import json
from pathlib import Path
import tarfile


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()


def read(path):return json.loads(path.read_bytes())


def backup(scope,work,archive,previous_backup):
    assert not archive.exists() and not (scope/'private_cache_backup.json').exists()
    assert read(scope/'independent_verification.json')['status']=='passed'
    assert read(scope/'run_receipt.json')['operational_locks_released'] is True
    previous=read(previous_backup)
    excluded={'collector.lock','lease_published','collector_pid.json'}
    with ExitStack() as stack:
        locks=sorted(set(read(work/'historical_locks.json'))|{str(work/'collector.lock')})
        for name in locks:
            f=stack.enter_context(Path(name).open('a+'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        files=[p for p in sorted(work.rglob('*')) if p.is_file() and p.name not in excluded]
        assert files and not any(p.is_symlink() for p in files)
        entries=[dict(path=work.name+'/'+p.relative_to(work).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
        manifest=dict(schema_version=1,private=True,entries=entries,
            restore_policy='Verify archive and each entry before evidence reuse. Restore into a fresh workspace; never revive old lease/ready/lock/PID state. New traffic needs a distinct pinned scope and fresh live locks/lease/cooldown.',
            required_prior_layer=dict(file_name=previous['file_name'],bytes=previous['bytes'],sha256=previous['sha256'],
                purpose='Prior-layer reproduction and before/after coverage comparison; current working responses are included in this archive.'))
        data=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
        with tarfile.open(archive,'w:gz') as tf:
            for p,e in zip(files,entries):tf.add(p,arcname=e['path'],recursive=False)
            member=tarfile.TarInfo('PRIVATE_CACHE_MANIFEST.json');member.size=len(data);member.mode=0o600
            tf.addfile(member,io.BytesIO(data))
    with tarfile.open(archive) as tf:
        assert len(tf.getmembers())==len(entries)+1
        for e in entries:
            body=tf.extractfile(e['path']).read()
            assert len(body)==e['bytes'] and hashlib.sha256(body).hexdigest()==e['sha256']
    meta=dict(schema_version=1,file_name=archive.name,bytes=archive.stat().st_size,sha256=sha(archive),
        private=True,private_files_verified=len(entries),source_work_folders=[work.name],
        operational_flags_excluded=True,public_repository_contains_no_raw_caches=True,saved_privately=False,
        required_predecessor_archive=manifest['required_prior_layer'],
        scope_protocol_sha256=sha(scope/'protocol.json'))
    (scope/'private_cache_backup.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
    return meta


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['scope','work','archive','previous_backup']:parser.add_argument(name,type=Path)
    args=parser.parse_args()
    print(json.dumps(backup(args.scope.resolve(),args.work.resolve(),args.archive.resolve(),args.previous_backup.resolve()),sort_keys=True))
