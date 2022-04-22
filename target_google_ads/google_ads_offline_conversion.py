from target_google_ads.utils import decimal_to_float


def dummy_conversion(msg):
    return msg


def click_conversions(client, customer, message):
    """
    Build a click conversion
    :param client: Google Ads Api client
    :param customer: Dictionary of Google Ads Account Id & Converion Action Id
    :param message: Conversion message in json format
    :return: click conversion
    """

    click_conversion = client.get_type("ClickConversion")
    conversion_action_service = client.get_service("ConversionActionService")
    click_conversion.conversion_action = (
        conversion_action_service.conversion_action_path(
            customer["customer_id"], message["conversion_action_id"]
        )
    )

    # Sets the single specified ID field.
    """
    gclid: The Google Click Identifier ID. If set, the wbraid and gbraid parameters must be None.
    wbraid: The WBRAID for the iOS app conversion. If set, the gclid and gbraid parameters must be None.
    gbraid: The GBRAID for the iOS app conversion. If set, the gclid and wbraid parameters must be None.
    """
    if "gclid" in message:
        click_conversion.gclid = message["gclid"]
    elif "gbraid" in message:
        click_conversion.gbraid = message["gbraid"]
    else:
        click_conversion.wbraid = message["wbraid"]

    click_conversion.conversion_value = decimal_to_float(message["conversion_value"])
    click_conversion.conversion_date_time = message["conversion_date_time"]
    click_conversion.currency_code = (
        message["currency_code"] if message["currency_code"] else "US"
    )

    if "external_attribution_model" in message and "external_attribution_credit" in message and message["external_attribution_credit"]:
        external_attribution_data = client.get_type("ExternalAttributionData")
        external_attribution_data.external_attribution_model = message["external_attribution_model"]
        external_attribution_data.external_attribution_credit = decimal_to_float(message["external_attribution_credit"])
        click_conversion.external_attribution_data = external_attribution_data

    if "conversion_custom_variables" in message:
        conversion_custom_variables = message["conversion_custom_variables"]
        for key in conversion_custom_variables:
            conversion_custom_variable = client.get_type("CustomVariable")
            conversion_custom_variable.conversion_custom_variable = key
            conversion_custom_variable.value = conversion_custom_variables[key]
            click_conversion.custom_variables.append(conversion_custom_variable)

    return click_conversion
