import os


class __Config(object):
    @property
    def BOT_TOKEN(self):
        return os.environ.get('BOT_TOKEN', '')

    @property
    def DEBUG(self):
        return os.environ.get('DEBUG', '').lower() == 'true'


config = __Config()
