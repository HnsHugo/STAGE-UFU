import unittest
from dual_api_native_frontier import collect_native
from dual_api_frontier import PROVIDERS
from test_independent_mempool_bridge import tx
class NativeResumeContracts(unittest.TestCase):
 def setUp(self):self.record=dict(address='source',payment_txid='reference',cutoff_height=10,cutoff_block_hash='block-10');self.anchor=tx('reference',10)
 def test_actual_cursor_used_even_when_sorted_union_has_different_last_txid(self):
  calls=[];saved=[]
  def get(key,path):
   calls.append(path)
   return self.anchor['status']if key.startswith('reference_')else []
  result=collect_native(self.record,self.anchor,[tx('actual',5),tx('zzz',5)],PROVIDERS[1],get,saved.append,cursor='actual')
  self.assertEqual(calls[1],'/address/source/txs/chain/actual');self.assertTrue(result['pagination_exhausted']);self.assertIsNone(result['features'])
 def test_same_provider_overlap_is_rejected_without_checkpoint(self):
  saved=[]
  def get(key,path):return self.anchor['status']if key.startswith('reference_')else [tx('actual',5)]
  with self.assertRaises(ValueError):collect_native(self.record,self.anchor,[tx('actual',5)],PROVIDERS[1],get,saved.append,cursor='actual')
  self.assertEqual(saved,[])
if __name__=='__main__':unittest.main()
