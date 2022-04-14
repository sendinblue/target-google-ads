import http
import json
import urllib

import pkg_resources
import singer
from google.ads.googleads.client import GoogleAdsClient
from jsonschema.validators import Draft4Validator

from target_google_ads.utils import float_to_decimal, walk_schema_for_numeric_precision

logger = singer.get_logger()


class GoogleAdsClient:
    def __init__(self, config, conversion_id):
        self.config = config
        self.batch_size = 500
        try:
            self.customer = json.loads(config["customer"])
        except TypeError:  # falling back to raw value
            self.customer = config["customer"]
        self.conversion_id = conversion_id
        self.client = self.__get_client()

    def __get_client(self):
        """
        Get google ads client
        """

        CONFIG = {
            "use_proto_plus": False,
            "developer_token": self.config["developer_token"],
            "client_id": self.config["oauth_client_id"],
            "client_secret": self.config["oauth_client_secret"],
            "refresh_token": self.config["refresh_token"],
        }

        client = GoogleAdsClient.load_from_dict(CONFIG, version=self.config["version"])

        return client

    def send_data(self, data):
        """
        Send data to google ads API
        :param data: List of click conversions
        :return: conversion response
        """
        conversion_upload_service = self.client.get_service("ConversionUploadService")
        request = self.client.get_type("UploadClickConversionsRequest")
        request.customer_id = self.customer["customer_id"]
        request.conversions = data
        request.partial_failure = True
        conversion_upload_response = conversion_upload_service.upload_click_conversions(
            request=request,
        )

        return conversion_upload_response

    def build_conversions(self, conversion_custom_variables, message, click_type):
        """
        Build a click conversion
        :param conversion_custom_variables: dictionary of custom variables
        :param message: conversion message in json format
        :param click_type: either a gclid, WBRAID, or GBRAID identifier can be passed into this
                example. See the following for more details:
                https://developers.google.com/google-ads/api/docs/conversions/upload-clicks
        :return: click conversion
        """
        click_conversion = self.client.get_type("ClickConversion")
        conversion_action_service = self.client.get_service("ConversionActionService")
        click_conversion.conversion_action = conversion_action_service.conversion_action_path(
            self.customer["customer_id"], self.customer["conversion_action_id"]
        )

        # Sets the single specified ID field.
        if click_type.equals("WBRAID"):
            click_conversion.wbraid = click_type
        elif click_type.equals("GBRAID"):
            click_conversion.gbraid = click_type
        else:
            click_conversion.gclid = click_type

        click_conversion.conversion_value = round(message["prediction"], 2)
        click_conversion.conversion_date_time = message["conversion_date_time"].strftime("%Y%m%d %H%M%S Etc/GMT")
        click_conversion.currency_code = self.config["currency_code"] if self.config["currency_code"] else "US"

        for key in conversion_custom_variables:
            conversion_custom_variable = self.client.get_type("CustomVariable")
            conversion_custom_variable.conversion_custom_variable = (key)
            conversion_custom_variable.value = conversion_custom_variables[key]
            click_conversion.custom_variables.append(conversion_custom_variable)

        return conversion_custom_variable

    def writes_messages(self, tap_stream):
        """
        For every line in tap_stream:
            - parses JSON
        :param messages:
        :return:
        """
        state = None
        data = []
        schemas = {}
        key_properties = {}
        validators = {}

        for line in tap_stream:
            try:
                message = singer.parse_message(line).asdict()
            except json.decoder.JSONDecodeError:
                logger.error("Unable to parse:\n{}".format(line))
                raise

            # Handle single record in message
            if isinstance(message, singer.RecordMessage):
                stream = message.stream
                if stream not in schemas:
                    raise Exception(
                        "A record for stream {} was encountered before a corresponding schema".format(stream))

                # Get the record from message
                record = self.build_conversions(message.record)
                data.append(record)

                # Send data to REST server
                data.append(record)
                if len(data) >= self.batch_size:
                    self.send_data(data)
                    data = []

                state = None

            elif isinstance(message, singer.StateMessage):
                state = message.value
                logger.debug(f'Setting state to {state}')
            elif isinstance(message, singer.SchemaMessage):
                stream = message.stream
                schemas[stream] = message.schema
                schema = float_to_decimal(schemas[stream])

                walk_schema_for_numeric_precision(schema)

                validators[stream] = Draft4Validator(message.schema)
                key_properties[stream] = message.key_properties
            else:
                raise Exception(f'Unknown message type {message.type} in message {message}')

        # Send last batch that is smaller then batch_size (for cases when data_size % batch_size != 0)
        # TODO: This seem a little slopy, maybe better would be cover this directly in loop over the lines
        if len(data) > 0:
            self.send_data(data)

        return state

    def send_usage_stats(self):
        """
        Send anonymous usage data to singer.io
        """
        try:
            version = pkg_resources.get_distribution('target-rest-api').version
            conn = http.client.HTTPConnection('collector.singer.io', timeout=10)
            conn.connect()
            params = {
                'e': 'se',
                'aid': 'singer',
                'se_ca': 'target-rest-api',
                'se_ac': 'open',
                'se_la': version,
            }
            conn.request('GET', '/i?' + urllib.parse.urlencode(params))
            response = conn.getresponse()
            conn.close()
        except:
            logger.debug('Collection request failed')
