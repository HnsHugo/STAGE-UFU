import unittest
from collect_binance_research_seed import resolve


class EvidenceTests(unittest.TestCase):
    def test_matching_identifier_alone_is_insufficient(self):
        tx={'vout':[{'scriptpubkey_address':'bc1qexamplev3wm','value':1}]}
        with self.assertRaises(ValueError):resolve(tx)

    def test_ambiguous_match_is_rejected(self):
        output={'scriptpubkey_address':'bc1qexamplev3wm','value':56799700000}
        with self.assertRaises(ValueError):resolve({'vout':[output,output]})


if __name__=='__main__':unittest.main()
