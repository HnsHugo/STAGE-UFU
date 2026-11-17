import copy
from datetime import datetime,timezone
import tempfile
from pathlib import Path
import unittest
from dual_api_frontier import collect_switch,eligible_providers,exclusive_run,PROVIDERS
from test_independent_mempool_bridge import tx

class DualAPIContracts(unittest.TestCase):
    def setUp(self):
        self.record=dict(address='source',payment_txid='reference',cutoff_height=10,cutoff_block_hash='block-10')
        self.anchor=tx('reference',10);self.old=[tx('newer',8),tx('a',5),tx('b',5)]
    def fetch(self,pages):
        def get(key,endpoint):
            if key.startswith('reference_'):return self.anchor['status']
            if key=='bridge':return tx('newer',8)
            result=pages[int(key[-4:])]
            if isinstance(result,Exception):raise result
            return result
        return get
    def test_both_directions_reconcile_intra_block_order_without_duplicate_coverage(self):
        for provider in PROVIDERS:
            saved=[];r=collect_switch(self.record,self.anchor,self.old,provider,
                self.fetch([[tx('b',5),tx('a',5),tx('c',5),tx('older',4)],[]]),saved.append)
            self.assertEqual((r['new_transactions'],r['verified_overlap']),(2,2))
            self.assertEqual(len({t['txid']for t in r['transactions']}),5)
            self.assertEqual(r['actual_native_cursor'],'older');self.assertIsNone(r['features'])
    def test_failure_after_saved_page_preserves_exact_frontier(self):
        saved=[]
        with self.assertRaises(OSError):collect_switch(self.record,self.anchor,self.old,PROVIDERS[1],
            self.fetch([[tx('b',5),tx('c',4)],OSError('503')]),saved.append)
        self.assertEqual(len(saved),1);self.assertEqual(saved[0]['actual_native_cursor'],'c')
    def test_conflicting_overlap_does_not_advance_checkpoint(self):
        saved=[]
        with self.assertRaisesRegex(ValueError,'Conflicting'):collect_switch(self.record,self.anchor,self.old,
            PROVIDERS[1],self.fetch([[tx('b',5,99)]]),saved.append)
        self.assertFalse(saved)
    def test_checkpoint_failure_stops_before_next_get(self):
        calls=[]
        def checkpoint(snapshot):raise OSError('disk full')
        get=self.fetch([[tx('c',4)]])
        def fetch(key,path):calls.append(key);return get(key,path)
        with self.assertRaises(OSError):collect_switch(self.record,self.anchor,self.old,PROVIDERS[0],fetch,checkpoint)
        self.assertEqual(calls,['reference_before','bridge','page_0000'])
    def test_own_provider_cooldowns_and_denials_are_not_reset_by_switch(self):
        now=datetime(2026,11,17,tzinfo=timezone.utc)
        gates={PROVIDERS[0]:dict(next_network_attempt_not_before='2026-11-18T00:00:00+00:00')}
        self.assertEqual(eligible_providers(gates,now),[PROVIDERS[1]])
        gates[PROVIDERS[1]]=dict(last_http_status=403)
        self.assertEqual(eligible_providers(gates,now),[])
    def test_second_worker_cannot_acquire_global_lock(self):
        with tempfile.TemporaryDirectory()as d:
            path=Path(d)/'global.lock'
            with exclusive_run([path]):
                with self.assertRaises(BlockingIOError):
                    with exclusive_run([path]):pass
            with exclusive_run([path]):pass
if __name__=='__main__':unittest.main()
