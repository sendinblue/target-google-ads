from tests import unittestcore


class TestSimpleStream(unittestcore.BaseUnitTest):
    def test_config(self):
        from target_google_ads import parse_config

        self.init_config('simple_stream.json',  'target-config.json')
        ret = parse_config()
        self.assertEqual(7, len(ret), msg="Count number of config fields")
        self.assertEqual("v10", ret["api_version"], msg="Google Ads Api version")

    def test_offline_conversion(self):
        import target_google_ads.google_ads_offline_conversion

        conversion_handler = getattr(
            target_google_ads.google_ads_offline_conversion, "dummy_conversion"
        )

        self.assertIsNotNone(conversion_handler)
        ret = conversion_handler(msg="I'm dummy message.")
        self.assertEqual("I'm dummy message.", ret)

    def test_simple_input(self):
        import io
        import sys
        import singer

        from target_google_ads import parse_config

        self.init_config('simple_stream.json', 'target-config.json')
        ret = parse_config()

        tap_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        count_lines = 0
        for line in tap_stream:
            message = singer.parse_message(line)
            self.assertTrue(isinstance(message, singer.RecordMessage))
            self.assertEqual("simple_stream", message.stream)
            record = message.record
            self.assertTrue(record["user_id"] in [4378219, 4378361])
            count_lines += 1
        self.assertEqual(2, count_lines, msg="Count number inputs")

    def test_check_conversion_id_in_message(self):
        import io
        import sys
        import singer
        from target_google_ads import parse_config
        from target_google_ads.google_ads_handler import GoogleAdsHandler

        self.init_config('combo_300_stream.json', 'integration-config.json')
        config = parse_config()
        client = GoogleAdsHandler(config)

        tap_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        for line in tap_stream:
            message = singer.parse_message(line)
            self.assertTrue(client.check_conversion_id(config, message.record))


