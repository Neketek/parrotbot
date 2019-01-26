from gevent import monkey
monkey.patch_all()


def start():
    import time
    from slackclient import SlackClient
    from slackclient.server import SlackConnectionError
    from modules.config.env import config as envconf
    from modules.config import server as servconf
    from modules.controller.core import actions
    from modules.controller.scheduled.manager import Manager
    from modules.model import sql
    from modules.logger import root as logger
    import threading
    sql.create_all()
    client = SlackClient(envconf.BOT_TOKEN)
    if client.rtm_connect():
        logger.info(
            'Established connection with Slack! Observing message queue...'
        )
        Manager(client).start(threading.current_thread())
        while client.server.connected:
            try:
                messages = client.rtm_read()
                actions.feed(client, messages)
                time.sleep(1)
            except SlackConnectionError:
                for i in range(servconf.RECONNECT_ATTEMPTS):
                    logger.error(
                        "Connection with slack was interrupted. "
                        + "Trying to reconnect in {}s. Attempt:{}".format(
                            servconf.RECONNECT_TIME_INTERVAL,
                            i+1
                        )
                    )
                    time.sleep(servconf.RECONNECTION_TIME_INTERVAL)
                    if client.rtm_connect():
                        break
                else:
                    break
    else:
        logger.error("Can't connect to Slack.")


if __name__ == '__main__':
    start()
