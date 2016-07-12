import logging
import json


logger = logging.getLogger('koppeltaal.connector')
logger.setLevel(logging.DEBUG)


critical = logger.critical
debug = logger.debug
error = logger.error
info = logger.info
warn = logger.warn


requests_logger = logging.getLogger("requests.packages.urllib3")
requests_logger.setLevel(logging.DEBUG)


def debug_json(message, **data):
    if 'json' in data:
        data['json'] = json.dumps(data['json'], indent=2, sort_keys=True)
    debug(message.format(**data))
