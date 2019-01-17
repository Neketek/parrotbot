from modules.config.env import config as envconf
import logging

root = logging.getLogger('server')
root.setLevel(logging.DEBUG if envconf.DEBUG else logging.INFO)
