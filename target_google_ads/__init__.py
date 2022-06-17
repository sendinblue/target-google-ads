#!/usr/bin/env python3
import argparse
import io
import json
import logging
import sys
import threading

import singer
import target_google_ads.google_ads_offline_conversion as google_ads_offline_conversion
from google.ads.googleads.errors import GoogleAdsException
from target_google_ads.google_ads_handler import GoogleAdsHandler
from target_google_ads.utils import emit_state, send_usage_stats

LOGGER = singer.get_logger()


REQUIRED_CONFIG_KEYS = [
    "oauth_client_id",
    "oauth_client_secret",
    "refresh_token",
    "customer_id",
    "conversion_id",
    "developer_token",
    "api_version",
    "offline_conversion",
]


def main_impl(config):
    LOGGER.info(f"Checking required config.")
    singer.utils.check_config(config, REQUIRED_CONFIG_KEYS)

    conversion = config["conversion_id"]
    conversion_handler = getattr(
        google_ads_offline_conversion, config["offline_conversion"]
    )

    LOGGER.info(f"Sync writing to google-ads api {config['api_version']} version.")
    tap_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    LOGGER.debug(f"Customer config : {conversion}")
    client = GoogleAdsHandler(config)
    state = client.writes_messages(config=config, tap_stream=tap_stream, conversion_handler=conversion_handler)
    # write a state file
    emit_state(state)

    LOGGER.info("Sync Completed")


def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file')
    args = parser.parse_args()

    if args.config:
        with open(args.config) as input:
            config = json.load(input)
    else:
        config = {}
    return config


def main():

    google_logger = logging.getLogger("google")
    google_logger.setLevel(level=logging.CRITICAL)

    try:
        config = parse_config()

        if not config.get("disable_collection", False):
            LOGGER.info(
                "Sending version information to singer.io. "
                + "To disable sending anonymous usage data, set "
                + 'the config parameter "disable_collection" to true'
            )
            threading.Thread(target=send_usage_stats).start()

        main_impl(config)
    except Exception as e:
        for line in str(e).splitlines():
            LOGGER.critical(line)
        raise e


if __name__ == "__main__":
    try:
        main()
    except GoogleAdsException as ex:
        LOGGER.error(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )

        for error in ex.failure.errors:
            LOGGER.error(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    LOGGER.error(f"\t\tOn field: {field_path_element.field_name}")
