from modules.controller.scheduled.report_requests import plan
from modules.controller.scheduled.report_requests import send
from modules.model import sql

session = sql.Session()
plan.update(session)
send.send(None, session, plan.load())
