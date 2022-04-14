import json
import os
import sys
import singer
from decimal import Decimal
import decimal

logger = singer.get_logger()


def emit_state(state):
    """
    Given a state, writes the state to a state file (e.g., state.json.tmp)
    :param state: state with bookmarks dictionary
    """
    if state is not None:
        line = json.dumps(state)
        logger.debug('Emitting state {}'.format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()


def float_to_decimal(value):
    '''
    Walk the given data structure and turn all instances of float
    into double.
    '''
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, list):
        return [float_to_decimal(child) for child in value]
    if isinstance(value, dict):
        return {k: float_to_decimal(v) for k, v in value.items()}
    return value


def numeric_schema_with_precision(schema):
    if 'type' not in schema:
        return False
    if isinstance(schema['type'], list):
        if 'number' not in schema['type']:
            return False
    elif schema['type'] != 'number':
        return False
    if 'multipleOf' in schema:
        return True
    return 'minimum' in schema or 'maximum' in schema


def get_precision(key, schema):
    v = abs(Decimal(schema.get(key, 1))).log10()
    if v < 0:
        return round(math.floor(v))
    return round(math.ceil(v))


def walk_schema_for_numeric_precision(schema):
    if isinstance(schema, list):
        for v in schema:
            walk_schema_for_numeric_precision(v)
    elif isinstance(schema, dict):
        if numeric_schema_with_precision(schema):
            scale = -1 * get_precision('multipleOf', schema)
            digits = max(get_precision('minimum', schema), get_precision('maximum', schema))
            precision = digits + scale
            if decimal.getcontext().prec < precision:
                logger.debug('Setting decimal precision to {}'.format(precision))
                decimal.getcontext().prec = precision
        else:
            for v in schema.values():
                walk_schema_for_numeric_precision(v)
