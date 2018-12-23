from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from .update_subscribers import update_subscribers


ERROR = """
Can't update subscribers.
{}
"""

SUCCESS = """
Subscribers cache updated.
Subscribers.
{}
"""

INITIAL = """
Updating subscribers cache...
"""


@a.register(c.command('update', 'subs'))
@sql.session()
def subscribers(c, session=None):
    try:
        c.reply(INITIAL, code_block=True)
        update_subscribers(c, session)
        session.commit()
        subs = session\
            .query(sql.Subscriber)\
            .all()
        msg = c.reply(
            SUCCESS.format(
                sql.Subscriber.to_pretty_table(subs)
            ),
            code_block=True
        ).get('message')
        return c.result().wait(msg)
    except ValueError as e:
        msg = c.reply(ERROR.format(e)).get('message')
        return c.result().wait(msg)
