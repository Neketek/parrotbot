from modules.controller.core import actions as a, Conditions as c
from modules.config.naming import short
from modules.model import sql
from sqlalchemy.orm import exc as orme
from . import reports


NO_QUEEST_TITLE = """
Pls, provide questionnaire title.
Ex. "ls questions <title>".
"""

NO_QUEST_WITH_NAME = """
Can't find questionnaire "{0}".
"""


@a.register(c.command(short.method.list, short.name.question))
@sql.session()
def question(c, session=None):
    try:
        name = c.cs_command_args[2]
    except IndexError:
        msg = c.reply_code(NO_QUEEST_TITLE).get('message')
        return c.result().wait(msg)
    try:
        quest = session\
            .query(sql.Questionnaire)\
            .filter(sql.Questionnaire.name == name)\
            .one()
    except orme.NoResultFound:
        msg = c.reply_code(NO_QUEST_WITH_NAME.format(name)).get('message')
        return c.result().wait(msg)
    result = "Questionnaire '{0}'.\n Questions:\n"
    n = 1
    for q in quest.questions:
        result += "\t {0}) {1}\n".format(n, q.text)
        n += 1
    result = result.format(name)
    msg = c.reply_code(result).get('message')
    return c.result().wait(msg)


@a.register(c.command(short.method.list, short.name.questionnaire))
@sql.session()
def quest(c, session=None):
    quests = session\
        .query(sql.Questionnaire)\
        .order_by(sql.Questionnaire.id.asc())\
        .all()
    result = "Questionnairies:\n{}"
    msg = (
        c.reply_code(
            result.format(
                sql.Questionnaire.to_pretty_table(quests)
            )
        ).get('message')
    )
    return c.result().wait(msg)


@a.register(c.command('ls', 'subs'))
@sql.session()
def subscriber(c, session=None):
    pass


@a.register(c.command('ls', 'ss'))
def subscription(c, session=None):
    pass
