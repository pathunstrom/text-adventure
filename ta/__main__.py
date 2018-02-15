import logging
from os import environ

from ta import Engine

TA_LOGGING = environ.get("TA_LOGGING")
log_level = getattr(logging, TA_LOGGING, "WARNING")
logging.basicConfig(level=log_level)

Engine().run()
