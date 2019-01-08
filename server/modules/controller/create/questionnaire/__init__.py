from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from .download_template import download_template
from .save import save
from modules.config.naming import short
from modules.controller import permission


INITITAL_MSG = """
Starting questionarie creation.
Waiting for questionarie template file...
"""

REPEAT_CONFIRMATION = """
yes|no?
"""

ERROR = """
Creation Stoped.
Error:
{0}
"""


@a.register(c.command(short.method.create, short.name.questionnaire))
@sql.session()
@permission.admin()
def quest(c, session=None):
    try:
        if c.i is None:
            return c.reply_and_wait(INITITAL_MSG).interactive('file')
        elif c.i.next == 'file':
            return download_template(c)
        elif isinstance(c.i.next, dict):
            if c.command == 'yes':
                return save(c, session, c.i.next)
            elif c.command == 'no':
                return c.reply_and_wait('Creation stopped.')
            else:
                return (
                    c.reply_and_wait(REPEAT_CONFIRMATION)
                    .interactive(c.i.next)
                )
    except ValueError as e:
        return c.reply_and_wait(ERROR.format(e))
