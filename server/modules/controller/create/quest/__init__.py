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
        print("QUEST")
        if c.i is not None:
            print("c.i.next", c.i.next)
        if c.i is None:
            msg = c.reply(INITITAL_MSG).get('message')
            return c.result().interactive('file').wait(msg)
        elif c.i.next == 'file':
            return download_template(c)
        elif isinstance(c.i.next, dict):
            if c.command == 'yes':
                return save(c, c.i.next)
            elif c.command == 'no':
                msg = c.reply('Creation stopped.').get('message')
                return c.result().wait(msg)
            else:
                msg = c.reply(REPEAT_CONFIRMATION).get('message')
                return c.result().interactive(c.i.next).wait(msg)
    except ValueError as e:
        msg = c.reply(ERROR.format(e)).get('message')
        return c.result().wait(msg)
