from modules.controller.core import actions as a, Conditions as c
from .request_report import request_report

NO_TITLE = """
Pls, provide questionnaire title.
Ex. create report <title>.
"""

ERROR = """
Can create reports.
Error:
{0}
"""


@a.register(c.command('create', 'report'))
def report(
    c
):
    try:
        title = c.cs_command_args[2]
    except IndexError:
        c.reply(NO_TITLE)
        return
    try:
        return request_report(c, title=title)
    except ValueError as e:
        c.reply(
            ERROR.format(e)
        )
        return
