from datetime import datetime,timedelta,timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from prepare_frontier_checkpoint import write
import recorded_remaining_campaign as campaign
import remaining_access_checkpoint as access


class RemainingContracts(unittest.TestCase):
    def access_fixture(self,directory,available=True,saved=True,closed=False):
        base=Path(directory);out=base/'access';out.mkdir()
        write(out/'coverage_audit.json',dict(status='passed',access_available=available))
        write(out/'private_cache_backup.json',dict(saved_privately=saved,library_metadata_applied=saved))
        write(base/'policy.json',dict(provider_access_policies={campaign.PROVIDER:dict(no_new_probe_authorized=closed,operational_validation_required=False)},
            latest_mempool_access_validation='access/coverage_audit.json'))
        return base

    def test_failed_provider_access_cannot_prepare_collection(self):
        with tempfile.TemporaryDirectory()as directory:
            base=self.access_fixture(directory,closed=True)
            with patch.object(campaign,'BASE',base),patch.object(campaign,'POLICY',base/'policy.json'):
                with self.assertRaises(AssertionError):campaign.validated_access()

    def test_successful_but_unsaved_access_cannot_prepare_collection(self):
        with tempfile.TemporaryDirectory()as directory:
            base=self.access_fixture(directory,saved=False)
            with patch.object(campaign,'BASE',base),patch.object(campaign,'POLICY',base/'policy.json'):
                with self.assertRaises(AssertionError):campaign.validated_access()

    def test_validated_saved_access_allows_distinct_preparation(self):
        with tempfile.TemporaryDirectory()as directory:
            base=self.access_fixture(directory)
            with patch.object(campaign,'BASE',base),patch.object(campaign,'POLICY',base/'policy.json'):
                self.assertEqual(campaign.validated_access(),base/'access')

    def test_all_fifty_are_included_once_in_uniform_small_units(self):
        candidates=[dict(source_id=f's{i:02d}',kind=['native','legacy_bridge','mixed_resume'][i%3],
            previous_bound=[278,32,39][i%3],historical_full_current_counter=100-i)for i in range(50)]
        chosen,units=campaign.build_units(candidates)
        ids=sum((u['source_ids']for u in units),[])
        self.assertEqual(len(chosen),50);self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(set(ids),{c['source_id']for c in candidates})
        by_id={c['source_id']:c for c in candidates}
        self.assertTrue(all(1<=len(u['source_ids'])<=3 for u in units))
        self.assertTrue(all(all((by_id[s]['kind'],by_id[s]['previous_bound'])==(u['kind'],u['previous_bound'])for s in u['source_ids'])for u in units))
        minimum=[min(by_id[s]['historical_full_current_counter']for s in u['source_ids'])for u in units]
        self.assertEqual(minimum,sorted(minimum))

    def test_access_counter_rejects_other_identity(self):
        with self.assertRaises(AssertionError):access.counter_check(dict(address='expected'),dict(address='other',chain_stats=dict(tx_count=1)))

    def test_access_counter_rejects_noninteger_or_negative_count(self):
        for value in [True,-1,1.5,'1']:
            with self.subTest(value=value),self.assertRaises(AssertionError):
                access.counter_check(dict(address='expected'),dict(address='expected',chain_stats=dict(tx_count=value)))

    def test_access_cannot_authorize_before_saved_cooldown(self):
        with tempfile.TemporaryDirectory()as directory:
            out=Path(directory);write(out/'protocol.json',dict(network_not_before=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()))
            with patch.object(access,'OUT',out),patch.object(access.campaign,'authorize')as authorize:
                with self.assertRaises(AssertionError):access.authorize()
                authorize.assert_not_called()


if __name__=='__main__':unittest.main()
