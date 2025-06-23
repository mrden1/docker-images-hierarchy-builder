import logging
import sys

from hierarchy_builder import config

#
# The logger and the logging level
#
logger = logging.getLogger(__name__)
level = getattr(logging, config.log_level.upper(), logging.INFO)
logger.setLevel(level)

#
# Exit handler
#
class ExitHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        if record.levelno in (logging.ERROR, logging.CRITICAL):
            sys.exit(1)
eh = ExitHandler()
logger.addHandler(eh)

#
# Logging format
#
fmt = '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
encoding = "utf-8"
formatter = logging.Formatter(fmt, datefmt)
eh.setFormatter(formatter)
