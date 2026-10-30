"""Protect source joins, evidence tiers and outcome/predictor separation."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import tempfile
import unittest

from consolidate_source_dataset import build, distribution, event_observation, join
import source_cohort as cohort


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT/'source_dataset_20261030/protocol.json'


class SourceDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(PROTOCOL.read_bytes())
        inputs = cls.protocol['inputs']
        _, cls.records = cohort.plan(ROOT/inputs['cohort_protocol']['file'])
        cls.state = json.loads((ROOT/inputs['checkpoint']['file']).read_bytes())
        cls.comparisons = json.loads((ROOT/inputs['corroboration']['file']).read_bytes())['rows']
        cls.reports = json.loads((ROOT/inputs['owner_reports']['file']).read_bytes())['rows']
        registry = json.loads((ROOT/inputs['registry_protocol']['file']).read_bytes())
        cls.payments = {r['txid']: r for r in json.loads(gzip.decompress(
            (ROOT/registry['history_file']).read_bytes()))['transactions']}

    def joined(self, comparisons=None, reports=None):
        return join(self.records, self.state,
                    self.comparisons if comparisons is None else comparisons,
                    self.reports if reports is None else reports, self.payments, 'coldcard_2026')

    def test_reports_do_not_propagate_and_predictors_remain_frozen(self):
        rows = self.joined()
        self.assertEqual(len(rows), 500)
        self.assertEqual([r['source_id'] for r in rows if r['labels']['reported_loss']==1], ['cohort_0002'])
        for r in rows:
            self.assertEqual(r['features'], self.state['entries'][r['source_id']]['features'])
            self.assertIsNone(r['labels']['independently_verified_compromise'])
            self.assertIsNone(r['labels']['independently_verified_seed_origin'])
            self.assertIsNone(r['labels']['hardware_signing_at_event'])
            self.assertFalse(r['verified_target_training_eligible'])
            self.assertTrue(set(r['features']).isdisjoint(r['event_evidence']))
            self.assertNotIn('reported_loss', r['features'])
            if r['source_id'] != 'cohort_0002':
                self.assertIsNone(r['labels']['reported_loss'])

    def test_duplicate_missing_or_misassigned_case_evidence_is_rejected(self):
        for changed in (self.comparisons+[self.comparisons[0]], self.comparisons[1:]):
            with self.assertRaises(ValueError): self.joined(comparisons=changed)
        for key, value in [('address_sha256','x'*64), ('payment_txid_sha256','x'*64), ('cutoff_height',1)]:
            changed = deepcopy(self.comparisons)
            changed[0][key] = value
            with self.assertRaises(ValueError): self.joined(comparisons=changed)

    def test_owner_mismatch_duplicates_and_label_promotions_are_rejected(self):
        with self.assertRaises(ValueError): self.joined(reports=self.reports+self.reports)
        for key,value in [('source_id','cohort_0001'), ('incident_group','another_case'),
                          ('independently_verified_compromise_label',1), ('verified_target_training_eligible',True)]:
            changed=deepcopy(self.reports);changed[0][key]=value
            with self.assertRaises(ValueError): self.joined(reports=changed)
        changed=deepcopy(self.comparisons);changed[0]['hardware_seed_origin_label']='Coldcard'
        with self.assertRaises(ValueError): self.joined(comparisons=changed)

    def test_partial_spend_is_preserved_as_address_outcome(self):
        row = next(r for r in self.joined() if r['source_id']=='cohort_0435')
        obs = row['event_evidence']
        self.assertFalse(obs['consumes_all_known_prior_block_utxos'])
        self.assertEqual((obs['known_prior_block_utxo_count'],obs['known_prior_block_utxos_consumed']), (225,200))
        self.assertEqual(obs['known_prior_block_value_not_consumed_sat'], 18606869)
        self.assertEqual(obs['known_prior_block_value_consumed_sat']+
                         obs['known_prior_block_value_not_consumed_sat'], row['features']['balance_sat'])

    def test_reference_anchor_and_prior_outpoint_values_are_checked(self):
        record=self.records[0];entry=self.state['entries'][record['pilot_id']]
        comparison=self.comparisons[0]
        changed=deepcopy(self.payments[record['payment_txid']]);changed['status']['block_height']+=1
        with self.assertRaises(ValueError): event_observation(record,entry,changed,comparison)
        changed=deepcopy(self.payments[record['payment_txid']]);changed['vin'][0]['prevout']['value']+=1
        with self.assertRaises(ValueError): event_observation(record,entry,changed,comparison)

    def test_missing_fees_are_not_zero_and_quantiles_are_observed_values(self):
        profile=distribution([None,1,2,3,4])
        self.assertEqual((profile['missing'],profile['zeros'],profile['p50'],profile['p95']), (1,0,2,4))
        self.assertIsNone(distribution([None])['p50'])
        with self.assertRaises(ValueError): distribution([float('inf')])
        for row in self.joined():
            if row['features']['spending_tx_count']==0:
                self.assertIsNone(row['features']['median_spending_tx_fee_rate_sat_vb'])

    def test_public_inputs_reproduce_exactly_and_wrong_pin_is_rejected(self):
        for name,raw in build(PROTOCOL).items():
            self.assertEqual(raw,(PROTOCOL.parent/name).read_bytes())
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path=Path(folder)/'protocol.json';changed=deepcopy(self.protocol)
            changed['inputs']['checkpoint']['sha256']='0'*64
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError,'Pinned input changed'):build(path)


if __name__=='__main__':unittest.main()
