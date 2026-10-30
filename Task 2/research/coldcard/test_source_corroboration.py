"""Reject approximate joins and keep case association separate from labels."""
import copy
from datetime import datetime, timezone
import unittest

from corroborate_sources import btc_sat, compare


class CorroborationTests(unittest.TestCase):
    def fixture(self):
        record=dict(pilot_id='cohort_0001',address='source',address_sha256='s'*64,
                    payment_txid='t'*64,cutoff_height=42)
        timestamp=int(datetime(2026,7,30,tzinfo=timezone.utc).timestamp())
        payment=dict(status=dict(block_height=42,block_hash='b'*64,block_time=timestamp),
                     vin=[dict(prevout=dict(value=10)),dict(prevout=dict(value=20))],
                     vout=[dict(scriptpubkey_address='collector',value=27)],fee=3)
        observations=[dict(spent_input_value_sat=10),dict(spent_input_value_sat=20)]
        addresses=[dict(address='source',btc_lost='0.00000030',utxos='2')]
        inputs=[dict(address='source',btc_lost=value,sweep_txid='t'*64,block='42',collector='collector')
                for value in ('0.00000010','0.00000020')]
        transactions=[dict(txid='t'*64,block_height='42',block_hash='b'*64,
                           block_time_utc='2026-07-30T00:00:00Z',input_count='2',input_value_sats='30',
                           output_count='1',cluster_output_value_sats='27',fee_sats='3',
                           destination_or_intermediate_address='collector',classification='sweep-funding-tx')]
        return [record,payment,observations,addresses,inputs,transactions,'collector']

    def test_exact_case_agreement_does_not_promote_theft_or_device_labels(self):
        result=compare(*self.fixture())
        self.assertTrue(result['both_external_reconstructions_agree'])
        self.assertEqual(result['case_relation'],'source_attributed')
        self.assertIsNone(result['independently_verified_compromise_label'])
        self.assertIsNone(result['hardware_seed_origin_label'])
        self.assertIsNone(result['hardware_signing_at_event_label'])
        self.assertFalse(result['supervised_training_eligible'])
        self.assertFalse(result['external_previous_outpoint_ids_available'])

    def test_equal_total_is_insufficient_when_input_multiset_differs(self):
        args=self.fixture()
        for row in args[4]:row['btc_lost']='0.00000015'
        result=compare(*args)
        self.assertTrue(result['somax_gross_value_and_utxo_count_agree'])
        self.assertFalse(result['somax_payment_input_value_multiset_agrees'])
        self.assertEqual(result['case_relation'],'graph_candidate')

    def test_duplicate_input_value_cannot_replace_a_missing_input(self):
        args=self.fixture();args[4]=[copy.deepcopy(args[4][0]),copy.deepcopy(args[4][0])]
        self.assertFalse(compare(*args)['both_external_reconstructions_agree'])

    def test_wrong_payment_block_or_collector_is_not_a_match(self):
        for field,value in [('sweep_txid','x'*64),('block','43'),('collector','another')]:
            args=self.fixture();args[4][0][field]=value
            self.assertFalse(compare(*args)['both_external_reconstructions_agree'])

    def test_second_reconstruction_requires_exact_satoshis_and_anchors(self):
        for field,value in [('fee_sats','4'),('block_hash','x'*64),('input_count','3'),
                            ('cluster_output_value_sats','28'),('block_time_utc','2026-07-30T00:00:01Z')]:
            args=self.fixture();args[5][0][field]=value;result=compare(*args)
            self.assertFalse(result['alva_integer_and_anchor_fields_agree'][field])
            self.assertFalse(result['both_external_reconstructions_agree'])

    def test_ambiguous_or_absent_external_payment_is_not_accepted(self):
        for transactions in ([],self.fixture()[5]*2):
            args=self.fixture();args[5]=transactions
            result=compare(*args)
            self.assertFalse(result['both_external_reconstructions_agree'])
            self.assertIsNone(result['independently_verified_compromise_label'])

    def test_btc_conversion_is_exact_and_rejects_fractional_satoshis(self):
        self.assertEqual(btc_sat('0.48000000'),48_000_000)
        self.assertEqual(btc_sat('0.00000001'),1)
        for value in ('0.000000001','-0.1','NaN','Infinity'):
            with self.assertRaises(ValueError):btc_sat(value)


if __name__=='__main__':unittest.main()
