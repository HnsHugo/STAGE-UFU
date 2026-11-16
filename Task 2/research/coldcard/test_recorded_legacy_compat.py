from copy import deepcopy
import unittest
from recorded_legacy_compat import provider_metadata


class LegacyMetadataCompatibilityTests(unittest.TestCase):
    def test_original_legacy_shape_has_a_protocol_bound_provider_without_mutation(self):
        marker=dict(source_id='comparison',key='reference',http_status=200,sha256='a'*64,endpoint_sha256='b'*64)
        before=deepcopy(marker)
        value=provider_metadata(marker,dict(provider='https://blockstream.info/api'))
        self.assertEqual(value['provider'],'https://blockstream.info/api')
        self.assertEqual(marker,before)
        self.assertEqual({k:v for k,v in value.items() if k!='provider'},before)

    def test_explicit_conflicting_provider_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'conflicts'):
            provider_metadata(dict(provider='https://mempool.space/api'),dict(provider='https://blockstream.info/api'))

    def test_unexpected_protocol_cannot_supply_a_fallback(self):
        with self.assertRaisesRegex(ValueError,'Unexpected'):
            provider_metadata(dict(http_status=200),dict(provider='https://other.invalid/api'))


if __name__=='__main__':unittest.main()
