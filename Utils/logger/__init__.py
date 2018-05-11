import os
import logging
import logging.config

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("example02")

logger.debug('This is debug message')
logger.info('This is info message')
logger.warning('This is warning message')