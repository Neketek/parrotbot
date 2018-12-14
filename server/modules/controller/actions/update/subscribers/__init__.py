from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from .update_subscribers import update_subscribers


ERROR = """
Can't update subscribers.
{}
"""

SUCCESS = """
Subscribers cache updated.
Subscribers:
{}
"""

INITIAL = """
Updating subscribers cache...
"""


@a.register(c.command('update', 'subscribers'))
@sql.session()
def subscribers(c, session=None):
    try:
        c.reply(INITIAL)
        update_subscribers(c, session)
        subs = session\
            .query(sql.Subscriber)\
            .all()
        result = ""
        n = 1
        for s in subs:
            result += "\t{0}) {1}\n".format(n, s.name)
            n += 1
        c.reply(SUCCESS.format(result))
    except ValueError as e:
        c.reply(ERROR.format(e))
