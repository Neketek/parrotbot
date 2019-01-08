from modules.model import sql
from sqlalchemy.orm import exc as orme
from functools import wraps

SUB_NOT_FOUND = """
Can't find you in subscribers cache.
Pls, ask slack or bot admin to update subscribers cache.
"""

NOT_ADMIN = """
You need to be slack or bot admin to perform this operation.
"""


def admin(context_pos=0, sql_session_key='session'):
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
            except orme.NoResultsFound:
                raise c.reply_and_wait(SUB_NOT_FOUND)
        return wrapper
    return decorator
