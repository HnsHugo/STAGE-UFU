"""Do not even import the guarded collector before the protocol's cooldown."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path


def cooldown_due(protocol, now):
    due = datetime.fromisoformat(protocol['network_not_before'])
    if due.tzinfo is None or now.tzinfo is None:
        raise ValueError('Timezone-aware cooldown and current time required')
    return now >= due


def main(protocol_path, output, work):
    protocol = json.loads(protocol_path.read_bytes())
    if not cooldown_due(protocol, datetime.now(timezone.utc)):
        print('COOLDOWN_NOT_DUE_NO_HTTP', flush=True)
        return
    source = protocol_path.parent.parent / 'source_prefix_extension_20261109_01/run_scope.py'
    spec = importlib.util.spec_from_file_location('guarded_checkpoint_runner', source)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.main(protocol_path, output, work)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('work', type=Path)
    args = parser.parse_args()
    main(args.protocol.resolve(), args.output.resolve(), args.work.resolve())
