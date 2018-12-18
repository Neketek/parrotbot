from modules.model import sql
from sqlalchemy import func, and_, or_
from datetime import datetime
from pytz import timezone
from sqlalchemy.orm import exc as orme

NOT_SUBSCRIBER = '''
You are not a subscriber!
There is no record about you.
'''


def get_pending_reports(c, session):
    try:
        sub = (
            session
            .query(sql.Subscriber)
            .filter(sql.Subscriber.id == c.user)
            .one()
        )
        tz = timezone(sub.timezone)
    except orme.NoResultFound:
        raise ValueError(NOT_SUBSCRIBER)
    try:
        reports = (
            session
            .query(sql.Subscription)
            .join(
                sql.Report,
                and_(
                    sql.Subscription.subscriber_id == sub.id,
                    sql.Subscription.active,
                    sql.Subscription.id == sql.Report.subscription_id
                )
            )
        )
    except orme.NoResultFound:
        pass
    return reports
