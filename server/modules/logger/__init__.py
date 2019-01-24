from modules.config.env import config as envconf
import logging

root = logging.getLogger('server')
root.setLevel(logging.DEBUG if envconf.DEBUG else logging.ERROR)
if envconf.LOG_TO_FILE:
    root.setHandler(
        logging.handlers.TimedRotatingFileHandler(
            "log",
            when='D',
            interval=1,
            backupCount=7,
            delay=True,
            utc=True
        )
    )
