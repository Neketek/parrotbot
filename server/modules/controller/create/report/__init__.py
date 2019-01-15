from modules.controller.core import actions as a, Conditions as c
from .request_report import request_report
from modules.config.naming import short
from modules.controller.core import utils


__CMD = (short.method.create, short.name.report,)
__PARAMS = [
    "{}_name".format(short.name.questionnaire)
]
CMD = utils.cmd_str(*__CMD, params=__PARAMS)


NO_TITLE = """
Pls, provide questionnaire name.
{}
""".format(CMD)

ERROR = """
Can create reports.
Error:
{}
"""


@a.register(c.command(*__CMD))
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
