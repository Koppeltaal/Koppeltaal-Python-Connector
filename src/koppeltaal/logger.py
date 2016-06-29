import logging


logger = logging.getLogger('koppeltaal.connector')
logger.setLevel(logging.DEBUG)


critical = logger.critical
debug = logger.debug
error = logger.error
info = logger.info
warn = logger.warn


requests_logger = logging.getLogger("requests.packages.urllib3")
requests_logger.setLevel(logging.DEBUG)
