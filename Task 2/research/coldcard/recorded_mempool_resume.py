"""Conservative dispatch timing and two-clock evidence for a NEW pinned scope.

This runner does not reopen the stopped round-7 scope. A successor must pin this
file, declare the 5.25-second dispatch bound, and pass the usual published lease,
lock and provider gates. Original collectors and protocol hashes stay intact.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import urllib.error
import uuid

import independent_mempool_resume as collector
from independent_mempool_pilot import MempoolHTTP, PROVIDER, require
from prepare_frontier_checkpoint import read, sha, write

OriginalGuardedRequests = collector.GuardedRequests
MINIMUM_SECONDS = 5.25


class DispatchClock:
    def __init__(self, minimum_seconds=MINIMUM_SECONDS, monotonic_ns=time.monotonic_ns,
                 wall_now=None, sleep=None):
        import asyncio
        require(minimum_seconds >= MINIMUM_SECONDS, 'Dispatch margin cannot be reduced')
        self.minimum_ns = round(minimum_seconds * 1_000_000_000)
        self.monotonic_ns = monotonic_ns
        self.wall_now = wall_now or (lambda: datetime.now(timezone.utc))
        self.sleep = sleep or asyncio.sleep
        self.session_id = uuid.uuid4().hex
        self.previous = None
        self.sequence = 0

    async def reserve(self):
        # Recheck after sleeping: an early wake-up cannot consume the margin.
        while self.previous is not None:
            remaining = self.minimum_ns - (self.monotonic_ns() - self.previous['monotonic_ns'])
            if remaining <= 0:
                break
            await self.sleep(remaining / 1_000_000_000)
        mono = self.monotonic_ns()
        wall = self.wall_now()
        if self.previous is not None:
            elapsed = (wall - datetime.fromisoformat(self.previous['wall_at'])).total_seconds()
            require(elapsed >= 5, 'Wall-clock spacing changed before dispatch; no request sent')
        self.sequence += 1
        evidence = dict(session_id=self.session_id, sequence=self.sequence,
                        monotonic_ns=mono, wall_at=wall.isoformat(),
                        enforced_minimum_seconds=self.minimum_ns / 1_000_000_000)
        self.previous = evidence
        return dict(evidence)


class RecordedHTTP(MempoolHTTP):
    async def start(self):
        await super().start()
        self.dispatch_clock = DispatchClock(max(MINIMUM_SECONDS, self.interval))
        self.last_dispatch_evidence = None

    async def request(self, url, timeout):
        require(url.startswith(PROVIDER + '/'), 'Unapproved provider URL')
        async with self.lock:
            evidence = await self.dispatch_clock.reserve()
            self.last_dispatch_evidence = evidence
            self.last_dispatch_at = evidence['wall_at']
        bound = self.aiohttp.ClientTimeout(total=self.response_timeout_seconds,
            connect=self.response_timeout_seconds, sock_read=self.response_timeout_seconds)
        async with self.client.get(url, timeout=bound, allow_redirects=False) as response:
            if response.status != 200:
                raise urllib.error.HTTPError(url, response.status, response.reason, response.headers, None)
            return json.loads(await response.read())


class RecordedRequests(OriginalGuardedRequests):
    def get(self, record, key, endpoint):
        previous = getattr(self.http, 'last_dispatch_evidence', None)
        try:
            return super().get(record, key, endpoint)
        finally:
            marker = self.work / 'requests' / record['pilot_id'] / (key + '.json')
            if marker.exists():
                meta = read(marker)
                evidence = getattr(self.http, 'last_dispatch_evidence', None)
                dispatched = evidence is not None and evidence != previous
                meta['dispatch_not_attempted'] = not dispatched
                # Never attribute a previous request's timestamp to a preflight failure.
                meta['dispatch_at'] = evidence['wall_at'] if dispatched else None
                meta['dispatch_clock_evidence'] = dict(evidence) if dispatched else None
                write(marker, meta)


def verify_dispatch_evidence(markers):
    fresh = [m for m in markers if not m.get('offline_reused')]
    sent = [m for m in fresh if not m.get('dispatch_not_attempted')]
    require(all(isinstance(m.get('dispatch_clock_evidence'), dict) for m in sent),
            'Missing monotonic dispatch evidence')
    require(len({m['dispatch_clock_evidence']['session_id'] for m in sent}) <= 1,
            'More than one dispatch clock session in this scope')
    sent.sort(key=lambda m: m['dispatch_clock_evidence']['sequence'])
    previous = None
    for marker in sent:
        evidence = marker.get('dispatch_clock_evidence')
        require(isinstance(evidence, dict), 'Missing monotonic dispatch evidence')
        require(evidence['wall_at'] == marker['dispatch_at'], 'Wall dispatch evidence differs')
        require(evidence['enforced_minimum_seconds'] >= MINIMUM_SECONDS, 'Reduced dispatch bound')
        if previous is not None:
            require(evidence['session_id'] == previous['session_id'] and
                    evidence['sequence'] == previous['sequence'] + 1, 'Dispatch session/sequence differs')
            require(evidence['monotonic_ns'] - previous['monotonic_ns'] >= round(MINIMUM_SECONDS * 1e9),
                    'Monotonic dispatch spacing exceeded')
        else:
            require(evidence['sequence'] == 1, 'Missing initial dispatch evidence')
        previous = evidence
    for marker in fresh:
        if marker.get('dispatch_not_attempted'):
            require(marker.get('dispatch_clock_evidence') is None and marker.get('dispatch_at') is None
                    and 'error_type' in marker, 'Unsent intent has misleading dispatch evidence')
    return dict(status='passed',sent_requests=len(sent),unsent_intents=len(fresh)-len(sent),
                minimum_enforced_seconds=MINIMUM_SECONDS)


def run(protocol_path, work):
    q = read(protocol_path)
    require(q.get('dispatch_clock_evidence') == 'monotonic_ns_and_utc', 'New timing protocol required')
    require(q.get('enforced_dispatch_spacing_seconds') == MINIMUM_SECONDS, 'Dispatch margin not declared')
    require(0 < q['requests_per_second'] <= .2 and q['workers'] == 1 and q['timeout_seconds'] == 45,
            'Original rate, worker or timeout bounds changed')
    pin = q['inputs'].get('recorded_dispatch_runner')
    require(pin is not None and sha((protocol_path.parent / pin['file']).resolve()) == sha(Path(__file__)),
            'Recorded runner is not pinned')
    RecordedHTTP.response_timeout_seconds = q['timeout_seconds']
    collector.MempoolHTTP = RecordedHTTP
    collector.GuardedRequests = RecordedRequests
    collector.run(protocol_path, work)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('work', type=Path)
    args = parser.parse_args()
    run(args.protocol.resolve(), args.work.resolve())
