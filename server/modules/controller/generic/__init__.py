from modules.controller.core import actions as a, Conditions as c
from . import help


@a.register(c.default())
def default(c):
    c.reply("I dont understand you. Try asking for 'help' :)")
