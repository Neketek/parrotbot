from modules.model import sql
from sqlalchemy.orm import exc as orme
from functools import wraps
from sqlalchemy import func as sqlf


SUB_NOT_FOUND = """
Can't find you in subscribers cache.
Pls, ask slack or bot admin to update subscribers cache.
"""

NOT_ADMIN = """
You need to be slack or bot admin to perform this operation.
"""


def admin(context_pos=0, sql_session_key='session', allow_when_no_subs=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = kwargs[sql_session_key]
            c = args[context_pos]
            try:
                sub = (
                    session
                    .query(sql.Subscriber)
                    .filter(sql.Subscriber.id == c.user)
                    .one()
                )
                if not (sub.admin or sub.bot_admin):
                    return c.reply_and_wait(NOT_ADMIN)
                else:
                    return func(*args, **kwargs)
            except orme.NoResultFound:
                if allow_when_no_subs:
                    subs_count = (
                        session
                        .query(sqlf.count(sql.Subscriber.id))
                        .scalar()
                    )
                    if subs_count == 0:
                        return func(*args, **kwargs)
                return c.reply_and_wait(SUB_NOT_FOUND)
        return wrapper
    return decorator
