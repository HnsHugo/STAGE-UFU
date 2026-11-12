"""Use a declared longer response timeout in a distinct native-Mempool scope."""
import argparse
from pathlib import Path

import independent_mempool_resume as collector
from independent_mempool_pilot import MempoolHTTP
from prepare_frontier_checkpoint import read


class SlowResponseHTTP(MempoolHTTP):
    async def request(self, url, timeout):
        return await super().request(url, self.response_timeout_seconds)


def run(protocol_path, work):
    q = read(protocol_path)
    if not 15 < q['timeout_seconds'] <= 45:
        raise ValueError('Longer response timeout must stay within the declared bound')
    SlowResponseHTTP.response_timeout_seconds = q['timeout_seconds']
    collector.MempoolHTTP = SlowResponseHTTP
    collector.run(protocol_path, work)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('protocol', type=Path); p.add_argument('work', type=Path)
    a = p.parse_args(); run(a.protocol.resolve(), a.work.resolve())
