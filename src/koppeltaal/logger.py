# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import logging
import json

logger = logging.getLogger('koppeltaal.connector')
requests_logger = logging.getLogger("requests.packages.urllib3")

critical = logger.critical
debug = logger.debug
error = logger.error
info = logger.info
warning = logger.warning


def set_log_level(level):
    logger.setLevel(level)
    requests_logger.setLevel(level)


def debug_json(message, **data):
    if 'json' in data:
        data['json'] = json.dumps(data['json'], indent=2, sort_keys=True)
    debug(message.format(**data))
