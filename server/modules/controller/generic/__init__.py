from modules.controller.core import actions as a, Conditions as c


@a.register(c.command('help'))
def help(c):
    msg = (
        c.reply("Command args:{args}".format(args=c.command_args))
        .get('message')
    )
    return c.result().wait(msg)


@a.register(c.default())
def default(c):
    c.reply("I dont understand you. Try asking for 'help' :)")
