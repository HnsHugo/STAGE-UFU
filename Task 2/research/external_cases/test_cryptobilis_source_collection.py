"""Failure-oriented checks for the fixed sample and no-retry network guard."""
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
import urllib.error
from unittest.mock import patch

import select_cryptobilis_sources as select
import collect_cryptobilis_sources as collect


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.first={a:dict(address=a,cutoff_height=h) for a,h in [('a',1),('b',1),('c',1),('d',2)]}
        self.contract=dict(excluded_address_sha256=[select.ready.hashed('a')],salt='fixed:',
                           quotas=[dict(height=1,desired_comparisons=2),dict(height=2,desired_comparisons=2)])

    def test_exclusion_and_shortfall_without_borrowing(self):
        rows,strata=select.choose(self.first,self.contract)
        self.assertEqual({r['address'] for r in rows},{'b','c','d'})
        self.assertEqual([r['shortfall'] for r in strata],[0,1])

    def test_selection_does_not_read_features_or_history_success(self):
        expected=select.choose(self.first,self.contract)
        for i,r in enumerate(self.first.values()):
            r.update(features={'balance_sat':10**12-i},history_success=bool(i%2),score=i)
        actual=select.choose(self.first,self.contract)
        self.assertEqual([r['address'] for r in actual[0]],[r['address'] for r in expected[0]])

    def test_hashed_replay_rejects_exclusion_tamper(self):
        public=dict(sources=[dict(address_sha256=select.ready.hashed('a'),selection_key='a',excluded=False,cutoff_height=1)])
        with self.assertRaisesRegex(ValueError,'exclusion'):
            select.replay(public,self.contract)

    def test_hashed_replay_rejects_ambiguous_key(self):
        public=dict(sources=[dict(address_sha256=x,selection_key='same',excluded=False,cutoff_height=1) for x in ['x','y']])
        with self.assertRaisesRegex(ValueError,'tie'):
            select.replay(public,self.contract)


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.clock=datetime(2026,11,3,tzinfo=timezone.utc)
        self.policy=dict(collector_lease=dict(state='idle'),last_retry_delay_seconds=57600,
                         next_network_attempt_not_before='2026-11-02T00:00:00+00:00')

    def test_future_cooldown_blocks(self):
        self.policy['next_network_attempt_not_before']='2026-11-04T00:00:00+00:00'
        with self.assertRaisesRegex(ValueError,'cooldown'):
            collect.network_gate(self.policy,clock=self.clock)

    def test_unexpired_other_lease_blocks(self):
        self.policy['collector_lease']=dict(state='running',owner='other',expires_at='2026-11-04T00:00:00+00:00')
        with self.assertRaisesRegex(ValueError,'lease'):
            collect.network_gate(self.policy,owner='mine',clock=self.clock)

    def test_long_retry_after_is_not_capped(self):
        m=dict(http_status=429,finished_at=self.clock.isoformat(),retry_after='172800')
        result=collect.backoff(self.policy,[m])
        self.assertEqual(result['last_retry_delay_seconds'],86400)
        self.assertEqual(result['next_network_attempt_not_before'],'2026-11-05T00:00:00+00:00')

    def test_http_date_retry_after_is_not_capped(self):
        m=dict(http_status=429,finished_at=self.clock.isoformat(),retry_after='Fri, 06 Nov 2026 00:00:00 GMT')
        self.assertEqual(collect.backoff(self.policy,[m])['next_network_attempt_not_before'],'2026-11-06T00:00:00+00:00')

    def test_backoff_has_two_hour_minimum(self):
        self.policy['last_retry_delay_seconds']=0
        m=dict(http_status=429,finished_at=self.clock.isoformat())
        self.assertEqual(collect.backoff(self.policy,[m])['last_retry_delay_seconds'],7200)

    def test_consumed_block_marker_never_retries(self):
        with TemporaryDirectory() as tmp:
            work=Path(tmp);(work/'block_requests').mkdir()
            (work/'block_requests/1.json').write_text('{}')
            with patch.object(collect.urllib.request,'build_opener') as http:
                with self.assertRaisesRegex(ValueError,'Consumed'):
                    collect.collect_block(dict(height=1,hash='f'*64),work)
                http.assert_not_called()

    def test_queued_http_start_is_cancelled_after_429(self):
        async def scenario():
            calls=[]
            class Response:
                status=429;reason='Rate limited';headers={}
                async def __aenter__(self):return self
                async def __aexit__(self,*args):return False
            class Client:
                def get(self,url,**kwargs):calls.append(url);return Response()
            http=collect.GuardedHTTP(1)
            http.interval=.001;http.loop=asyncio.get_running_loop();http.lock=asyncio.Lock();http.next_start=0
            http.client=Client();http.aiohttp=SimpleNamespace(ClientTimeout=lambda **kw:kw,
                                                            ClientHttpProxyError=type('ProxyError',(Exception,),{}))
            result=await asyncio.gather(http.request('https://blockstream.info/api/tx/a',15),
                                        http.request('https://blockstream.info/api/tx/b',15),return_exceptions=True)
            self.assertEqual(len(calls),1)
            self.assertIsInstance(result[0],urllib.error.HTTPError)
            self.assertIsInstance(result[1],InterruptedError)
        asyncio.run(scenario())


if __name__ == '__main__':
    unittest.main()
