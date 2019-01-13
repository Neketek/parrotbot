from modules.controller.scheduled.report import plan
from modules.controller.scheduled.report import send
from modules.controller.core import Context
from modules.controller.core.time import get_utcnow
from slackclient import SlackClient
from modules.config.env import config as envconf
from modules.model import sql

client = SlackClient(envconf.BOT_TOKEN)
client.rtm_connect()
context = Context(client)

session = sql.Session()
plan.update(session)
send.send(context, session, plan.load(), get_utcnow().replace(
    day=8,
    hour=18,
    minute=0
))
