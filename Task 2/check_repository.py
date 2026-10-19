"""Check Task 2 navigation, preserved scientific artifacts and optional test suites."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parent
SUITES = {
    'coldcard': ('research/coldcard', 'test*.py'),
    'external_cases': ('research/external_cases', 'test*.py'),
    'wallet_storage': ('supplementary/wallet_storage', 'test*.py'),
    'ellipticplusplus': ('supplementary/ellipticplusplus', 'test*.py'),
    'real_cats': ('supplementary/real_cats', 'test*.py'),
    'demo': ('.', 'test_demo.py'),
}


def check():
    errors, count = [], 0
    for source in [REPOSITORY / 'README.md', *sorted(ROOT.rglob('*.md'))]:
        # Documentation examples inside code fences are not live Markdown links.
        text = re.sub(r'```[\s\S]*?```', '', source.read_text())
        for match in re.finditer(r'\]\(([^)\s]+)\)', text):
            target = match.group(1)
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            count += 1
            path = (source.parent / unquote(parts.path)).resolve()
            if not path.exists():
                errors.append(f'{source.relative_to(REPOSITORY)}: missing link target {target}')
    python_files = list(ROOT.rglob('*.py'))
    for path in python_files:
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as error:
            errors.append(str(error))
    manifest = json.loads((ROOT / 'docs/ARTIFACT_MANIFEST.json').read_text())
    for relative, expected in manifest['sha256'].items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append('Changed or missing preserved artifact: ' + relative)
    return {'internal_links_checked': count, 'python_files_parsed': len(python_files),
            'preserved_artifacts_checked': len(manifest['sha256']), 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests', action='store_true', help='Run the six offline suites in separate processes')
    parser.add_argument('--output', type=Path, help='Write a new check report; do not overwrite')
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        parser.error('Output already exists')
    report = check()
    if args.tests:
        report['test_suites'] = []
        for name, (folder, pattern) in SUITES.items():
            command = [sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT/folder), '-p', pattern]
            result = subprocess.run(command, cwd=REPOSITORY, capture_output=True, text=True, timeout=180)
            report['test_suites'].append({'suite':name,'command':command,'exit_code':result.returncode,
                                         'stdout':result.stdout,'stderr':result.stderr})
            print(name + ': ' + ('passed' if result.returncode == 0 else 'FAILED'), flush=True)
    failed = bool(report['errors']) or any(s['exit_code'] for s in report.get('test_suites', []))
    report['status'] = 'failed' if failed else 'passed'
    if args.output is not None:
        with args.output.open('x') as handle:
            json.dump(report, handle, indent=2); handle.write('\n')
    print(json.dumps({k:v for k,v in report.items() if k!='test_suites'}, indent=2))
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
