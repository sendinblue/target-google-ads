import decimal
import http
import json
import math
import sys
import urllib
from datetime import datetime

import pkg_resources
import singer

LOGGER = singer.get_logger()


def emit_state(state):
    """
    Given a state, writes the state to a state file (e.g., state.json.tmp)
    :param state: state with bookmarks dictionary
    """
    if state is not None:
        line = json.dumps(state)
        LOGGER.debug("Emitting state {}".format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()


def decimal_to_float(value):
    """
    Walk the given data structure and turn all instances of double
    into float.
    """
    if isinstance(value, decimal.Decimal):
        return float(str(value))
    if isinstance(value, list):
        return [decimal_to_float(child) for child in value]
    if isinstance(value, dict):
        return {k: decimal_to_float(v) for k, v in value.items()}
    return value


def numeric_schema_with_precision(schema):
    if "type" not in schema:
        return False
    if isinstance(schema["type"], list):
        if "number" not in schema["type"]:
            return False
    elif schema["type"] != "number":
        return False
    if "multipleOf" in schema:
        return True
    return "minimum" in schema or "maximum" in schema


def get_precision(key, schema):
    v = abs(decimal(schema.get(key, 1))).log10()
    if v < 0:
        return round(math.floor(v))
    return round(math.ceil(v))


def walk_schema_for_numeric_precision(schema):
    if isinstance(schema, list):
        for v in schema:
            walk_schema_for_numeric_precision(v)
    elif isinstance(schema, dict):
        if numeric_schema_with_precision(schema):
            scale = -1 * get_precision("multipleOf", schema)
            digits = max(
                get_precision("minimum", schema), get_precision("maximum", schema)
            )
            precision = digits + scale
            if decimal.getcontext().prec < precision:
                LOGGER.debug("Setting decimal precision to {}".format(precision))
                decimal.getcontext().prec = precision
        else:
            for v in schema.values():
                walk_schema_for_numeric_precision(v)


def send_usage_stats():
    """
    Send anonymous usage data to singer.io
    """
    try:
        version = pkg_resources.get_distribution("target-rest-api").version
        conn = http.client.HTTPConnection("collector.singer.io", timeout=10)
        conn.connect()
        params = {
            "e": "se",
            "aid": "singer",
            "se_ca": "target-rest-api",
            "se_ac": "open",
            "se_la": version,
        }
        conn.request("GET", "/i?" + urllib.parse.urlencode(params))
        conn.getresponse()
        conn.close()
    except Exception:
        LOGGER.debug("Collection request failed")


def datetime_to_ads_format(conversion_date):
    conversion_datetime = datetime.strptime(conversion_date, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S%z")

    timestamp_string = "{0}:{1}".format(
        conversion_datetime[:-2],
        conversion_datetime[-2:]
    )

    return timestamp_string