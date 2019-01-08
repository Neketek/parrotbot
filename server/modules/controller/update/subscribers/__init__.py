from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from .update_subscribers import update_subscribers
from modules.config.naming import short
from modules.controller import permission


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


@a.register(c.command(short.method.update, short.name.subscriber))
@sql.session()
@permission.admin()
def subscribers(c, session=None):
    try:
        c.reply(INITIAL, code_block=True)
        update_subscribers(c, session)
        session.commit()
        subs = session\
            .query(sql.Subscriber)\
            .all()
        return c.reply_and_wait(
            SUCCESS.format(
                sql.Subscriber.to_pretty_table(subs)
            ),
            code_block=True
        )
    except ValueError as e:
        return c.reply_and_wait(ERROR.format(e))
