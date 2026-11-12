"""Verify the complete split private archive; restore only plans and old frontier pages."""
import argparse
from contextlib import ExitStack
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import tarfile

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE/'source_prefix_extension_20261110_01'))
from prepare_scope import validate_cached
from recover_cache import records_from_primary


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()


class ConcatenatedParts:
    def __init__(self, streams):
        self.streams, self.index = streams, 0

    def read(self, size):
        if size < 0:raise ValueError('Unbounded compressed reads are disabled')
        result = bytearray()
        while len(result) < size and self.index < len(self.streams):
            block = self.streams[self.index].read(size-len(result))
            if block:result.extend(block)
            else:self.index += 1
        return bytes(result)


def restore(parts_directory, destination, resume_path, report_path):
    destination, report_path = destination.resolve(), report_path.resolve()
    assert not destination.exists() and not report_path.exists()
    backup_path = BASE/'source_prefix_extension_20261109_01/private_cache_backup.json'
    backup = read(backup_path)
    wanted = sorted(read(resume_path)['coldcard_unextended_at_16_page_bound_source_ids'])
    wanted_set = set(wanted)
    combined = hashlib.sha256(); total = 0; parts = []
    for item in backup['parts']:
        path = parts_directory/item['file_name']
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(8*1024*1024),b''):
                combined.update(block); total += len(block)
        parts.append(path)
    assert total == backup['bytes'] and combined.hexdigest() == backup['sha256']
    destination.mkdir(mode=0o700)
    observed, extracted, manifest_data = {}, [], None
    def selected(name):
        p = Path(name)
        if p.name == 'plan.json':return True
        if 'requests' not in p.parts:return False
        index = p.parts.index('requests')
        if len(p.parts) != index+3 or p.parts[index+1] not in wanted_set:return False
        if p.name in ['reference.json','reference.json.gz']:return True
        match = re.fullmatch(r'tail_(\d{4})\.json(?:\.gz)?',p.name)
        return bool(match and int(match[1]) < 16)
    with ExitStack() as stack:
        streams = [stack.enter_context(p.open('rb')) for p in parts]
        gz = stack.enter_context(gzip.GzipFile(fileobj=ConcatenatedParts(streams),mode='rb'))
        with tarfile.open(fileobj=gz,mode='r|') as archive:
            for member in archive:
                name = Path(member.name)
                assert not name.is_absolute() and '..' not in name.parts
                assert member.isfile() or member.isdir(), 'Links and special archive members are forbidden'
                if member.isdir():continue
                assert member.name not in observed
                is_manifest = member.name == 'PRIVATE_CACHE_MANIFEST.json'
                keep = selected(member.name) and name.name not in ['collector.lock','lease_published','collector_pid.json']
                target = destination/name
                output = None
                if keep:
                    assert target.is_relative_to(destination)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    output = target.open('xb'); extracted.append(member.name)
                h, count, chunks = hashlib.sha256(), 0, []
                with archive.extractfile(member) as stream:
                    for block in iter(lambda:stream.read(8*1024*1024),b''):
                        h.update(block); count += len(block)
                        if output:output.write(block)
                        if is_manifest:chunks.append(block)
                if output:output.close()
                assert count == member.size
                if is_manifest:manifest_data = b''.join(chunks)
                else:observed[member.name] = dict(bytes=count,sha256=h.hexdigest())
        while gz.read(8*1024*1024):pass
    expected_manifest = read(BASE/'source_prefix_extension_20261110_01/cache_restoration_verification.json')['primary_manifest_sha256']
    assert manifest_data and hashlib.sha256(manifest_data).hexdigest() == expected_manifest
    manifest = json.loads(manifest_data)
    assert len(manifest['entries']) == backup['private_files_verified'] == len(observed)
    assert len({x['path'] for x in manifest['entries']}) == len(observed)
    for item in manifest['entries']:
        assert observed[item['path']] == dict(bytes=item['bytes'],sha256=item['sha256'])
    (destination/'PRIVATE_CACHE_MANIFEST.json').write_bytes(manifest_data)
    records = records_from_primary(destination)
    candidates = sorted({p.parent for p in destination.rglob('plan.json')})
    details = []
    for sid in wanted:
        record = records[sid]
        options = [(validate_cached(record,folder,max_pages=16),folder) for folder in candidates]
        saved, folder = max(options,key=lambda x:len(x[0]))
        details.append(dict(source_id=sid,saved_reference=bool(saved),saved_tail_pages=max(0,len(saved)-1),
            reusable_responses=len(saved),cache_directory=folder.relative_to(destination).as_posix()))
    report = dict(schema_version=1,status='passed',archive_sha256=combined.hexdigest(),archive_bytes=total,
        primary_manifest_sha256=expected_manifest,all_primary_files_verified=len(observed),
        selected_files_restored=len(extracted),wanted_unextended_sources=len(wanted),
        sources_with_reusable_response=sum(bool(x['reusable_responses']) for x in details),
        source_ids_with_16_cached_pages=[x['source_id'] for x in details if x['saved_tail_pages']==16],
        next_twenty_source_ids=wanted[:20],per_source=details,operational_flags_restored=False,
        raw_histories_restored=False,provider_requests=0,model_fits=0,new_scores=0,
        inputs=dict(archive_backup_sha256=sha(backup_path),selection_resume_sha256=sha(resume_path),restoration_code_sha256=sha(Path(__file__))))
    report_path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return {k:v for k,v in report.items() if k not in ['per_source','source_ids_with_16_cached_pages']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['parts_directory','destination','resume_path','report_path']:parser.add_argument(key,type=Path)
    args = parser.parse_args()
    print(json.dumps(restore(args.parts_directory,args.destination,args.resume_path,args.report_path),sort_keys=True))
