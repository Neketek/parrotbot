from gevent import monkey
monkey.patch_all()


def start():
    import time
    from slackclient import SlackClient
    from modules.config.env import config as envconf
    from modules.controller.core import actions
    from modules.controller.scheduled.manager import Manager
    from modules.model import sql
    import threading
    client = SlackClient(envconf.BOT_TOKEN)
    print(actions)
    sql.create_all()
    if client.rtm_connect():
        Manager(client).start(threading.current_thread())
        while client.server.connected:
            messages = client.rtm_read()
            actions.feed(client, messages, envconf.DEBUG)
            time.sleep(1)
    else:
        print("Can't connect to slack")


if __name__ == '__main__':
    start()
