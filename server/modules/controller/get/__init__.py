from modules.controller.core import actions as a, Conditions as c


@a.register(c.command('ls, questions'))
def ls_questions(c):
    pass


@a.register(c.command('ls', 'quest'))
def ls_quest(c):
    pass


@a.register(c.command('help'))
def help(c):
    c.reply("Command args:{args}".format(args=c.command_args))


@a.register(c.default())
def default(c):
    c.reply("I dont understand you. Try asking for 'help' :)")
