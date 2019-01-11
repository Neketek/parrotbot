from modules.model import sql
from sqlalchemy import not_


def update_schedule(session):
    subs = (
        session
        .query(sql.Subscriber)
        .filter(sql.Subscriber.active)
        .filter(not_(sql.Subscriber.archived))
        .all()
    )
    timezones = set([s.tz for s in subs])
