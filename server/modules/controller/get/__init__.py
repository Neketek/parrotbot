from modules.controller.core import actions as a, Conditions as c


@a.register(c.command('help'))
def help(c):
    c.reply("No help yet!")


@a.register(c.default())
def default(c):
    c.reply("I dont understand you. Try asking for 'help' :)")
