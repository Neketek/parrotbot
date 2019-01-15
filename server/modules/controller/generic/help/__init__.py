from modules.controller.core import actions as a, Conditions as c


@a.register(c.command('help', cmd_str='help'))
def help(c):
    return c.reply_and_wait("LEN:{}".format(len(a.registered_cmd)))
