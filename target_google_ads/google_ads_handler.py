import json

import singer
from google.ads.googleads.client import GoogleAdsClient
from jsonschema.validators import Draft4Validator

from target_google_ads.error_handler import print_results
from target_google_ads.utils import walk_schema_for_numeric_precision, decimal_to_float

LOGGER = singer.get_logger()


class GoogleAdsHandler:
    def __init__(self, config, api_version):
        self.developer_token = config["developer_token"]
        self.oauth_client_id = config["oauth_client_id"]
        self.oauth_client_secret = config["oauth_client_secret"]
        self.refresh_token = config["refresh_token"]
        self.api_version = api_version

        self.batch_size = 500
        self.client = self.__get_client()

    def __get_client(self):
        """
        Get google ads client
        """

        CONFIG = {
            "use_proto_plus": True,
            "developer_token": self.developer_token,
            "client_id": self.oauth_client_id,
            "client_secret": self.oauth_client_secret,
            "refresh_token": self.refresh_token,
            # "validate_only": True,
        }

        client = GoogleAdsClient.load_from_dict(config_dict=CONFIG, version=self.api_version)

        return client

    def send_data(self, config: dict, data: list) -> None:
        """
        Send data to google ads API
        :param config: Dictionary of config
        :param data: List of click conversions
        :return: conversion response
        """
        conversion_upload_service = self.client.get_service("ConversionUploadService")
        request = self.client.get_type("UploadClickConversionsRequest")
        request.customer_id = str(config["customer_id"])
        request.conversions.extend(data)
        request.partial_failure = True
        conversion_upload_response = conversion_upload_service.upload_click_conversions(
            request=request,
        )

        print_results(self.client, conversion_upload_response)

    def writes_messages(self, config: dict, tap_stream, conversion_handler):
        """
        For every line in tap_stream:
            - parses JSON
        :param config: dict of config
        :param tap_stream: Inputs messages
        :param conversion_handler:
        :return:
        """
        state = None
        data = []
        schemas = {}
        key_properties = {}
        validators = {}

        for line in tap_stream:
            try:
                message = singer.parse_message(line)
            except json.decoder.JSONDecodeError:
                LOGGER.error("Unable to parse:\n{}".format(line))
                raise

            # Handle single record in message
            if isinstance(message, singer.RecordMessage):
                stream = message.stream

                if stream not in schemas:
                    raise Exception(f"A record for stream {stream} was encountered before a corresponding schema")

                # Get schema for this record's stream
                # schema = decimal_to_float(schemas[stream])

                msg = message.record
                # Validate record
                validators[stream].validate(decimal_to_float(msg))

                # Get the record from message
                record = conversion_handler(self.client, config, msg)

                # Send data to REST server
                data.append(record)
                if len(data) >= self.batch_size:
                    self.send_data(config, data)
                    data = []

                state = None

            elif isinstance(message, singer.StateMessage):
                state = message.value
                LOGGER.debug(f"Setting state to {state}")
            elif isinstance(message, singer.SchemaMessage):
                stream = message.stream
                schemas[stream] = message.schema
                schema = decimal_to_float(schemas[stream])

                walk_schema_for_numeric_precision(schema)

                validators[stream] = Draft4Validator(message.schema)
                key_properties[stream] = message.key_properties
            else:
                raise Exception(
                    f"Unknown message type {message['type']} in message {message}"
                )

        if len(data) > 0:
            self.send_data(config, data)

        return state
