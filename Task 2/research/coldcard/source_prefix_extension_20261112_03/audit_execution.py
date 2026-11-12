"""Run the unchanged raw/response auditor for this fixed scope."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'source_prefix_extension_20261112_01'))
from audit_execution import audit
if __name__ == '__main__':
    audit(ROOT / 'protocol.json', ROOT.parent / ('source_cohort_work_' + ROOT.name))
