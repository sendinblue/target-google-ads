from tests import unittestcore
import unittest


class TestGoogleAdsTarget(unittestcore.BaseUnitTest):
    def test_click_conversions(self):
        from target_google_ads import parse_config, main_impl

        self.init_config('combo_300_stream.json', 'integration-config.json')
        config = parse_config()
        main_impl(config)


if __name__ == '__main__':
    unittest.main()