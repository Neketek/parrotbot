from modules.controller.core import actions as a, Conditions as c


CMD_SELECTION_HEADER = """
Type cmd number to view cmd description
or `.stop` to exit interactive mode.
"""

NOT_NUMBER = """
{} is not a number or `.stop`.
"""


NOT_IN_RANGE = """
There is no cmd with number {}. Range: 1-{}
Pls, provide correct number.
"""

HELP_FORMAT = """
{}
{}
"""


def get_cmd_list():
    res = []
    for cmd, htext in a.registered_cmd:
        if htext is not None:
            res.append((cmd, htext,))
    res.sort(key=lambda c: c[0])
    return res


def create_available_cmd_selection_text():
    result = CMD_SELECTION_HEADER
    cmdlist = get_cmd_list()
    for i in range(len(cmdlist)):
        result += "\t{}. {}\n".format(i+1, cmdlist[i][0])
    return result


@a.register(c.command('help', cmd_str='help'))
def help(c):
    if c.i is None:
        return (
            c.reply_and_wait(create_available_cmd_selection_text())
            .interactive('select')
        )
    elif c.i.next == 'select':
        try:
            selected = int(c.command)
        except ValueError:
            if c.command == '.stop':
                return c.reply_and_wait('Stopped.')
            return (
                c.reply_and_wait(NOT_NUMBER.format(c.i.command))
                .interactive('select')
            )
        try:
            cmds = get_cmd_list()
            return c.reply_and_wait(HELP_FORMAT.format(*cmds[selected-1]))
        except IndexError:
            return c.reply_and_wait(NOT_IN_RANGE.format(selected, len(cmds)))
