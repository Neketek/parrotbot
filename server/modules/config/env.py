import os


class __Config(object):
    @property
    def BOT_TOKEN(self):
        return os.environ.get('BOT_TOKEN', '')

    @property
    def DEBUG(self):
        return os.environ.get('DEBUG', '').lower() == 'true'

    @property
    def DB_DEBUG(self):
        return os.environ.get('DB_DEBUG', '').lower() == 'true'

    @property
    def LOG_TO_FILE(self):
        return os.environ.get('LOG_TO_FILE', '').lower() == 'true'


config = __Config()
