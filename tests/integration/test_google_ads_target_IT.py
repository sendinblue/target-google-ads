from tests import unittestcore
import unittest
from target_google_ads import parse_config, main_impl


class TestGoogleAdsTarget(unittestcore.BaseUnitTest):
    def test_click_conversions(self):
        self.init_config('combo_300_stream.json', 'integration-config.json')
        config = parse_config()
        main_impl(config)

    def test_enhanced_conversions(self):
        self.init_config('npc_per_creation_date_enhanced.json', 'enhanced-config.json')
        config = parse_config()
        main_impl(config)


if __name__ == '__main__':
    unittest.main()
