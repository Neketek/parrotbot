from modules.controller.core import actions as a, Conditions as c
from .download_template import download_template

INITITAL_MSG = """
Starting questionarie creation.
Waiting for questionarie template file...
"""


@a.register(c.command('create', 'quest'))
def quest(c):
    if c.next is None:
        c.reply(INITITAL_MSG)
        return c.interactive('file')
    elif c.next == 'file':
        return download_template(c)
    elif isinstance(c.next, dict):
        c.reply("Stopping creation...")
