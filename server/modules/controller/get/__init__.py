from modules.controller.core import actions as a, Conditions as c


@a.register(c.command('help'))
def help(c):
    if c.next is None:
        c.reply("What help do you need?")
        return c.interactive(1)
    elif c.next < 3:
        c.reply("What?"*c.next)
        return c.interactive(c.next+1)
    else:
        c.reply("Can't help you with this :(")
        return None


@a.register(c.command('hello'))
def hello(c):
    if c.next and c.text.strip(' ').lower() == 'kve':
        c.reply("kuruk?")
        return
    else:
        c.reply("kve!")
        return c.interactive(True)


@a.register(c.default())
def default(c):
    c.reply("I dont understand you!")
