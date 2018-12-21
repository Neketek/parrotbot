from modules.controller.core import actions as a, Conditions as c
from .download_template import download_template
from .save import save


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


@a.register(c.command('create', 'quest'))
def quest(c):
    try:
        if c.i is None:
            c.reply(INITITAL_MSG)
            return c.interactive('file')
        elif c.i.next == 'file':
            return download_template(c)
        elif isinstance(c.i.next, dict):
            if c.command == 'yes':
                save(c, c.i.next)
                return
            elif c.command == 'no':
                c.reply('Creation stopped.')
                return
            else:
                c.reply(REPEAT_CONFIRMATION)
                return c.interactive(c.i.next)
    except ValueError as e:
        c.reply(ERROR.format(e))
