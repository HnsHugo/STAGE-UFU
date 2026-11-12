"""Run the independent export verifier against this scope's frozen baseline."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'source_prefix_extension_20261112_01'))
import verify_execution as verifier
verifier.ROOT = ROOT
if __name__ == '__main__':
    report = verifier.verify()
    (ROOT / 'independent_verification.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, sort_keys=True))
