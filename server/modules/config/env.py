import os


class __Config(object):
    @property
    def BOT_TOKEN(self):
        return 'xoxb-500317872951-499466546965-qMTNRy4E45lCcxHcryEkOv4v'

    @property
    def DEBUG(self):
        return os.environ.get('DEBUG', '').lower() == 'true'


config = __Config()
