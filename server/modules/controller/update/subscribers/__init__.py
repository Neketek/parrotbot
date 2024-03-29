from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from .update_subscribers import update_subscribers
from modules.config.naming import short
from modules.controller import permission
from modules.controller.core import utils
from .help_text import TEXT as HTEXT
from modules.controller.scheduled.report import plan

__CMD = (short.method.update, short.name.subscriber,)
CMD = utils.cmd_str(*__CMD)

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


@a.register(c.command(*__CMD, cmd_str=CMD, cmd_help=HTEXT))
@sql.session()
@permission.admin(allow_when_no_subs=True)
def subscribers(c, session=None):
    try:
        c.reply(INITIAL, code_block=True)
        update_subscribers(c, session)
        session.commit()
        plan.update(session)
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
