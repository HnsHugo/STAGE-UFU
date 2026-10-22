import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from rank_block_recipients import load_references, load_protocol, reproduce, target_features_from_history, FEATURES


class TransferTests(unittest.TestCase):
    def test_pinned_plain_json_history_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);raw=json.dumps({'address':'reference','transactions':[]}).encode()
            (root/'history.json').write_bytes(raw)
            protocol={'references':[dict(address='reference',history_file='history.json',history_sha256=hashlib.sha256(raw).hexdigest())]}
            self.assertEqual(load_references(protocol,root)['reference']['transactions'],[])
            (root/'history.json').write_bytes(raw+b' ')
            with self.assertRaisesRegex(ValueError,'checksum'):load_references(protocol,root)

    def test_snapshot_selection_is_earliest_receipt_not_highest_score(self):
        root=Path(__file__).resolve().parent
        protocol=load_protocol(root/'btcpay_transfer_protocol_20261022.json')
        histories=load_references(protocol,root)
        selected=set()
        for ref in protocol['references']:
            history=histories[ref['address']]
            positive=[t for t in history['transactions'] if t['status'].get('confirmed') and any(
                o.get('scriptpubkey_address')==ref['address'] and o['value']>0 for o in t['vout'])]
            selected.add(min(t['status']['block_height'] for t in positive))
        self.assertEqual(selected,{b['height'] for b in protocol['blocks']})

    def test_second_positive_output_is_not_removed_to_improve_score(self):
        root=Path(__file__).resolve().parent
        protocol=load_protocol(root/'btcpay_transfer_protocol_20261022.json')
        histories=load_references(protocol,root)
        ref=protocol['references'][1]
        row=target_features_from_history(histories[ref['address']],{b['hash'] for b in protocol['blocks']})
        self.assertEqual(row['receipt_transaction_count'],1)
        self.assertEqual(row[FEATURES[1]],0)
        diagnostics=json.loads((root/'btcpay_transfer_results_20261022/receipt_diagnostics.json').read_text())
        receipt=diagnostics['receipts'][1]['receipts'][0]
        self.assertEqual(receipt['output_values_sat'],[46608022,15258])

    def test_separate_transfer_ranks_reproduce_offline(self):
        root=Path(__file__).resolve().parent
        result=reproduce(root/'btcpay_transfer_results_20261022',root/'btcpay_transfer_protocol_20261022.json')
        self.assertEqual(result['cohorts'],1)
        self.assertTrue(result['reference_rankings_reproduced'])


if __name__=='__main__':unittest.main()
