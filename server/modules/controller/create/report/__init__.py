from modules.controller.core import actions as a, Conditions as c
from .request_report import request_report
from modules.config.naming import short
NO_TITLE = """
Pls, provide questionnaire name.
Ex. create report <name>.
"""

ERROR = """
Can create reports.
Error:
{0}
"""


@a.register(c.command(short.method.create, short.name.report))
def report(
    c
):
    try:
        name = c.cs_command_args[2]
    except IndexError:
        c.reply(NO_TITLE)
        return
    try:
        return request_report(c, name=name)
    except ValueError as e:
        c.reply(
            ERROR.format(e)
        )
        return
