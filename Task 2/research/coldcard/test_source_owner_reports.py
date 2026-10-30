"""Keep exact owner assertions, device claims and verified labels separate."""
import copy
import gzip
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from build_source_registry import digest, json_bytes
from adjudicate_owner_reports import assertion_bytes, build, map_report


class OwnerReportTests(unittest.TestCase):
    def fixture(self):
        record=dict(pilot_id='cohort_0001',address='source',address_sha256='s'*64,
                    payment_txid='t'*64,cutoff_height=42,cutoff_block_hash='b'*64)
        payment=dict(txid='t'*64,status=dict(block_height=42,block_hash='b'*64,block_time=1785375441),
                     vin=[dict(txid='a'*64,vout=0,prevout=dict(scriptpubkey_address='source',value=10)),
                          dict(txid='b'*64,vout=1,prevout=dict(scriptpubkey_address='source',value=20))],
                     vout=[dict(scriptpubkey_address='collector',value=27)],fee=3)
        prefix=[dict(received=[dict(outpoint_id=digest(('a'*64+':0').encode())),
                              dict(outpoint_id=digest(('b'*64+':1').encode()))],spent=[])]
        entries={'cohort_0001':dict(prefix=prefix)}
        report=dict(report_id='report_1',reporter_id_sha256='r'*64,address='source',payment_txid='t'*64,
                    declared_role='owner_source',first_person_wallet_address=True,first_person_loss_report=True,
                    reported_hardware=['Coldcard Mk3'],observed_by_project_on='2026-10-30',sources=[],caveats=[])
        return report,[record],{'t'*64:payment},entries

    def test_exact_owner_report_is_sourced_but_not_forensic_ground_truth(self):
        row=map_report(*self.fixture())
        self.assertEqual(row['source_id'],'cohort_0001')
        self.assertEqual(row['reported_loss_label'],1)
        self.assertEqual(row['reported_hardware_association_label'],'Coldcard')
        self.assertEqual(row['known_prior_block_utxos_consumed'],2)
        for field in ('independently_verified_compromise_label','independently_verified_seed_origin_label','hardware_signing_at_event_label'):
            self.assertIsNone(row[field])
        self.assertFalse(row['proof_of_control_verified'])
        self.assertFalse(row['verified_target_training_eligible'])

    def test_receiver_or_wrong_payment_cannot_label_a_source(self):
        for field,value in [('address','collector'),('payment_txid','x'*64)]:
            args=self.fixture();args[0][field]=value
            self.assertEqual(map_report(*args)['status'],'no_unique_exact_source_payment_match')

    def test_third_party_or_unspecified_role_is_not_an_owner_assertion(self):
        for field,value in [('first_person_loss_report',False),('first_person_wallet_address',False),('declared_role','collector')]:
            args=self.fixture();args[0][field]=value
            self.assertEqual(map_report(*args)['status'],'insufficient_first_person_source_assertion')

    def test_other_or_missing_hardware_is_not_renamed_coldcard(self):
        for models in ([],['Ledger Nano'],['Trezor']):
            args=self.fixture();args[0]['reported_hardware']=models;row=map_report(*args)
            self.assertEqual(row['reported_loss_label'],1)
            self.assertIsNone(row['reported_hardware_association_label'])

    def test_prior_address_outputs_are_not_an_entire_wallet_claim(self):
        args=self.fixture();args[3]['cohort_0001']['prefix'][0]['received'].append(dict(outpoint_id='another'))
        row=map_report(*args)
        self.assertFalse(row['consumes_all_known_prior_block_utxos'])
        self.assertEqual(row['known_prior_block_utxos_consumed'],2)
        self.assertEqual(row['known_prior_block_utxo_count'],3)

    def test_anchor_or_value_mismatch_rejects_corrupt_reference_evidence(self):
        for field,value in [('fee',4),('block_hash','x'*64)]:
            args=self.fixture();payment=args[2]['t'*64]
            if field=='fee':payment['fee']=value
            else:payment['status'][field]=value
            with self.assertRaises(ValueError):map_report(*args)

    def test_redacted_public_assertions_reconstruct_exactly_and_reject_tampering(self):
        report,records,_,_=self.fixture()
        assertions=dict(reports=[report]);raw=json_bytes(assertions)
        public=copy.deepcopy(assertions);row=public['reports'][0]
        row['address_sha256']=records[0]['address_sha256'];row.pop('address')
        row['payment_txid_sha256']=digest(row.pop('payment_txid').encode())
        payload=dict(original_input_sha256=digest(raw),assertions=public)
        protocol=dict(input_snapshot_file='missing.json',input_snapshot_sha256=digest(raw))
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);path=out/'redacted_assertions.json';path.write_bytes(json_bytes(payload))
            self.assertEqual(assertion_bytes(protocol,out,out,records),raw)
            payload['assertions']['reports'][0]['reported_hardware']=['Ledger']
            path.write_bytes(json_bytes(payload))
            with self.assertRaisesRegex(ValueError,'checksum mismatch'):
                assertion_bytes(protocol,out,out,records)

    def test_duplicate_posts_by_one_account_count_as_one_report(self):
        report,records,payments,entries=self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);out=root/'output';out.mkdir();inputs=root/'inputs';inputs.mkdir()
            duplicate=copy.deepcopy(report);duplicate['report_id']='report_2'
            assertions=dict(reports=[report,duplicate],lead_outcomes=[])
            raw=json_bytes(assertions);(inputs/'assertions.json').write_bytes(raw)
            (root/'cohort.json').write_bytes(b'{}')
            (root/'checkpoint.json').write_bytes(json_bytes(dict(entries=entries)))
            (root/'history.json.gz').write_bytes(gzip.compress(json_bytes(dict(transactions=list(payments.values())))))
            (root/'registry.json').write_bytes(json_bytes(dict(history_file='history.json.gz')))
            protocol=dict(reviewed_on='2026-10-30',input_snapshot_file='assertions.json',input_snapshot_sha256=digest(raw))
            for key,name in [('cohort_protocol','cohort.json'),('checkpoint','checkpoint.json'),('source_registry_protocol','registry.json')]:
                protocol[key+'_file']=name;protocol[key+'_sha256']=digest((root/name).read_bytes())
            path=out/'protocol.json';path.write_bytes(json_bytes(protocol))
            with patch('adjudicate_owner_reports.cohort.plan',return_value=({},records)),patch('adjudicate_owner_reports.cohort.validate'):
                result=build(path,inputs)
            self.assertEqual(result['summary']['duplicate_reports_collapsed'],1)
            self.assertEqual(result['summary']['owner_reported_loss_sources'],1)
            self.assertEqual(result['summary']['independently_verified_compromise_sources'],0)


if __name__=='__main__':unittest.main()
