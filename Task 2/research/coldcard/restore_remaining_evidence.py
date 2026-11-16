"""Verify complete saved archives, restoring only the three needed Coldcard layers."""
from pathlib import Path,PurePosixPath
import hashlib
import json
import tarfile

from prepare_frontier_checkpoint import read,sha,write

BASE=Path(__file__).resolve().parent
DOWNLOADS=Path('/workspace/scratch/fc897d43bfda/recovery/fifty_restored_20261116')
SCOPES=['source_prefix_extension_20261109_01','source_prefix_extension_20261112_01',
        'mempool_fifty_20261112_tail_bridge_20261113']


def restore():
    report=[]
    for scope in SCOPES:
        meta=read(BASE/scope/'private_cache_backup.json');archive=DOWNLOADS/meta['file_name']
        assert archive.stat().st_size==meta['bytes'] and sha(archive)==meta['sha256']
        work='source_cohort_work_'+scope
        with tarfile.open(archive)as tf:
            members={m.name:m for m in tf.getmembers()}
            manifests=[m for m in members.values()if Path(m.name).name=='PRIVATE_CACHE_MANIFEST.json']
            assert len(manifests)==1
            manifest=json.load(tf.extractfile(manifests[0]));entries=manifest['entries']
            assert len(entries)==meta['private_files_verified']
            verified=restored=existing=0
            for e in entries:
                name=e['path'];parts=PurePosixPath(name).parts
                assert not name.startswith('/')and '..'not in parts
                member=members[name];assert member.isfile()and member.size==e['bytes']
                digest=hashlib.sha256();data=tf.extractfile(member)
                target=None
                if work in parts and parts[-1]not in {'collector.lock','lease_published','collector_pid.json'}:
                    at=parts.index(work);target=BASE.joinpath(*parts[at:])
                elif parts[:2]==(scope,'private_work')and parts[-1]not in {'collector.lock','lease_published','collector_pid.json'}:
                    target=BASE.joinpath(work,*parts[2:])
                if target:
                    assert BASE in target.resolve().parents
                    target.parent.mkdir(parents=True,exist_ok=True)
                temporary=target.with_name(target.name+'.restore-new')if target and not target.exists()else None
                stream=temporary.open('wb')if temporary else None
                size=0
                try:
                    for block in iter(lambda:data.read(8*1024*1024),b''):
                        digest.update(block);size+=len(block)
                        if stream:stream.write(block)
                finally:
                    data.close()
                    if stream:stream.close()
                assert size==e['bytes']and digest.hexdigest()==e['sha256']
                verified+=1
                if temporary:
                    temporary.replace(target);restored+=1
                elif target:
                    assert sha(target)==e['sha256'];existing+=1
            assert restored+existing>0
        report.append(dict(scope=scope,archive=meta['file_name'],archive_bytes=meta['bytes'],
            archive_sha256=meta['sha256'],all_archive_files_verified=verified,needed_files_restored=restored,
            identical_existing_files=existing,operational_flags_not_restored=True))
        print(json.dumps(report[-1]),flush=True)
    out=BASE/'mempool_remaining_fifty_20261116';out.mkdir(exist_ok=True)
    write(out/'restoration_verification.json',dict(status='passed',archives=report,
        scope='Complete archive fingerprint verification; only the needed Coldcard work layers restored. No historical external-case experiment rerun.',provider_requests=0))


if __name__=='__main__':restore()
