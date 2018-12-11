import time
from slackclient import SlackClient
from modules.config.env import get_bot_token
from modules.model import sql
from modules.controller.core import actions


client = SlackClient(get_bot_token())

print(actions)

starterbot_id = None

if __name__ == '__main__':
    if client.rtm_connect():
        while client.server.connected:
            messages = client.rtm_read()
            actions.feed(client, messages)
            time.sleep(1)
    else:
        print("Can't connect to slack")
