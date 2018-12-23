from gevent import monkey
monkey.patch_all()
import time
from slackclient import SlackClient
from modules.config.env import config as envconf
from modules.controller.core import actions
from modules.model import sql
client = SlackClient(envconf.BOT_TOKEN)

print(actions)


sql.create_all()
starterbot_id = None

if __name__ == '__main__':
    if client.rtm_connect():
        while client.server.connected:
            messages = client.rtm_read()
            actions.feed(client, messages, envconf.DEBUG)
            time.sleep(1)
    else:
        print("Can't connect to slack")
