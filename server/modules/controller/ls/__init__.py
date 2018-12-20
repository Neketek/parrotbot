from modules.controller.core import actions as a, Conditions as c
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


@a.register(c.command('ls', 'questions'))
@sql.session()
def ls_questions(c, session=None):
    try:
        name = c.cs_command_args[2]
    except IndexError:
        c.reply_code(NO_QUEEST_TITLE)
        return
    try:
        quest = session\
            .query(sql.Questionnaire)\
            .filter(sql.Questionnaire.name == name)\
            .one()
    except orme.NoResultFound:
        c.reply_code(NO_QUEST_WITH_NAME.format(name))
        return
    result = "Questionnaire '{0}'.\n Questions:\n"
    n = 1
    for q in quest.questions:
        result += "\t {0}) {1}\n".format(n, q.text)
        n += 1
    result = result.format(name)
    c.reply_code(result)


@a.register(c.command('ls', 'quest'))
@sql.session()
def ls_quest(c, session=None):
    quests = session\
        .query(sql.Questionnaire)\
        .order_by(sql.Questionnaire.id.asc())\
        .all()
    result = "Questionnairies:\n{}"
    c.reply_code(result.format(sql.Questionnaire.to_pretty_table(quests)))


@a.register(c.command('ls', 'subscribers'))
@sql.session()
def ls_subscribers(c, session=None):
    subs = []
    result = None
    try:
        quest = session\
            .query(sql.Questionnaire)\
            .filter(sql.Questionnaire.name == c.cs_command_args[2])\
            .one()
        subs = [
            s.subscriber
            for
            s in quest.subscriptions
        ]
        result = 'Subscribers of "{}"\n{{}}'.format(c.cs_command_args[2])
    except IndexError:
        result = 'Subscribers\n{}'
        subs = session\
            .query(sql.Subscriber)\
            .all()
    except orme.NoResultFound:
        c.reply_code(NO_QUEST_WITH_NAME.format(c.cs_command_args[2]))
        return
    c.reply_code(result.format(sql.Subscriber.to_pretty_table(subs)))
