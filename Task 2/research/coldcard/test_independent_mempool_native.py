import copy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from independent_mempool_native import validate_page, check_lease
from independent_mempool_pilot import PROVIDER
from prepare_frontier_checkpoint import sha, write
from test_independent_mempool_bridge import tx


class NativeCoverageContracts(unittest.TestCase):
    def setUp(self):
        self.record = dict(address='source', payment_txid='reference', cutoff_height=10)

    def test_same_block_order_is_allowed_and_duplicate_tx_is_rejected(self):
        seen = {'reference'}
        self.assertEqual(validate_page(self.record, [tx('b', 8), tx('a', 8)], seen, 10), 8)
        with self.assertRaisesRegex(ValueError, 'Repeated'):
            validate_page(self.record, [tx('b', 8)], seen, 8)

    def test_unrelated_transaction_is_rejected(self):
        wrong = tx('unrelated', 8); wrong['vout'][0]['scriptpubkey_address'] = 'other'
        with self.assertRaisesRegex(ValueError, 'unrelated'):
            validate_page(self.record, [wrong], {'reference'}, 10)

    def test_forward_height_and_unconfirmed_data_are_rejected(self):
        for bad in [tx('newer', 9), tx('unconfirmed', 8)]:
            if bad['txid'] == 'unconfirmed':
                bad['status']['confirmed'] = False
            with self.assertRaisesRegex(ValueError, 'ordering'):
                validate_page(self.record, [bad], {'reference'}, 8)

    def test_oversized_page_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Invalid'):
            validate_page(self.record, [tx(str(i), 8) for i in range(26)], {'reference'}, 10)

    def test_empty_page_is_valid_without_manufacturing_transactions(self):
        seen = {'reference'}
        self.assertEqual(validate_page(self.record, [], seen, 10), 10)
        self.assertEqual(seen, {'reference'})

    def test_live_provider_cooldown_prevents_network_permission(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder); protocol = p / 'protocol.json'; policy = p / 'policy.json'
            q = dict(pass_name='native_test', blockstream_cooldown_preserved_until='old-blockstream-gate')
            write(protocol, q)
            lease = dict(state='running', owner=q['pass_name'], provider=PROVIDER,
                protocol_sha256=sha(protocol), expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())
            live = dict(collector_lease=lease, active_collection_scope=q['pass_name'], provider_access_policies={
                PROVIDER: {}, 'https://blockstream.info/api': dict(next_network_attempt_not_before='old-blockstream-gate')})
            write(policy, live); permit = dict(collector_lease=lease, published_commit='a' * 40)
            check_lease(q, protocol, permit, policy)
            live['provider_access_policies'][PROVIDER]['next_network_attempt_not_before'] = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
            write(policy, live)
            with self.assertRaisesRegex(ValueError, 'cooldown'):
                check_lease(q, protocol, permit, policy)

    def test_changed_live_owner_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder); protocol = p / 'protocol.json'; policy = p / 'policy.json'
            q = dict(pass_name='native_test', blockstream_cooldown_preserved_until='old-blockstream-gate'); write(protocol, q)
            lease = dict(state='running', owner=q['pass_name'], provider=PROVIDER, protocol_sha256=sha(protocol),
                expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())
            wrong = copy.deepcopy(lease); wrong['owner'] = 'other'
            write(policy, dict(collector_lease=wrong, active_collection_scope=q['pass_name']))
            with self.assertRaisesRegex(ValueError, 'Live native lease'):
                check_lease(q, protocol, dict(collector_lease=lease, published_commit='a' * 40), policy)


if __name__ == '__main__':
    unittest.main()
