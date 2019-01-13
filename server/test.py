from modules.controller.scheduled.report import plan
from modules.controller.scheduled.report import send
from modules.controller.core.time import get_utcnow
from modules.model import sql

session = sql.Session()
plan.update(session)
send.send(None, session, plan.load(), get_utcnow().replace(
    day=8,
    hour=18,
    minute=0
))
