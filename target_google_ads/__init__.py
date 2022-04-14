#!/usr/bin/env python3
import io
import logging
import sys
import threading

import singer
from singer import utils
from target_google_ads.google_ads_client import GoogleAdsClient
from target_google_ads.utils import emit_state

LOGGER = singer.get_logger()


REQUIRED_CONFIG_KEYS = [
    "oauth_client_id",
    "oauth_client_secret",
    "refresh_token",
    "customer_ids",
    "developer_token",
    "version",
    "custom_variable_id",
    "click_conversion_type",
    "currency_code"
]


def main_impl():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    LOGGER.info(f"Checking required config.")
    singer.utils.check_config(args.config, REQUIRED_CONFIG_KEYS)

    client = GoogleAdsClient(args.config)

    if not args.config.get('disable_collection', False):
        LOGGER.info('Sending version information to singer.io. ' +
                    'To disable sending anonymous usage data, set ' +
                    'the config parameter "disable_collection" to true')
        threading.Thread(target=client.send_usage_stats).start()

    LOGGER.info(f"Sync writing to google-ads api {args.config['version']} version.")
    tap_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    state = client.writes_messages(tap_stream)

    # write a state file
    emit_state(state)

    LOGGER.info("Sync Completed")


def main():

    google_logger = logging.getLogger("google")
    google_logger.setLevel(level=logging.CRITICAL)

    try:
        main_impl()
    except Exception as e:
        for line in str(e).splitlines():
            LOGGER.critical(line)
        raise e


if __name__ == "__main__":
    main()
