from modules.config.env import config as envconf
import logging
from logging import handlers

root = logging.getLogger('server')
root.setLevel(logging.DEBUG if envconf.DEBUG else logging.INFO)
if envconf.LOG_TO_FILE:
    fmt = logging.Formatter(
        '%(asctime)s|%(message)s'
    )
    handler = handlers.TimedRotatingFileHandler(
        "files/log/log",
        when='D',
        interval=1,
        backupCount=2,
        delay=True,
        utc=True
    )
    handler.setFormatter(fmt)
    root.propagate = False
    root.addHandler(handler)
