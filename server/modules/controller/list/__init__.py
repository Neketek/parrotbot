from modules.controller.core import actions as a, Conditions as c
from modules.config.naming import short
from modules.model import sql
from sqlalchemy.orm import exc as orme
from . import reports


NO_QUEEST_NAME = """
Pls, provide questionnaire name.
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
        return c.reply_and_wait(NO_QUEEST_NAME)
    try:
        quest = session\
            .query(sql.Questionnaire)\
            .filter(sql.Questionnaire.name == name)\
            .one()
    except orme.NoResultFound:
        return c.reply_and_wait(NO_QUEST_WITH_NAME.format(name))
    result = "Questionnaire '{0}'.\n Questions:\n"
    n = 1
    for q in quest.questions:
        result += "\t {0}) {1}\n".format(n, q.text)
        n += 1
    result = result.format(name)
    return c.reply_and_wait(result)


@a.register(c.command(short.method.list, short.name.questionnaire))
@sql.session()
def questionnaire(c, session=None):
    quests = session\
        .query(sql.Questionnaire)\
        .order_by(sql.Questionnaire.id.asc())\
        .all()
    return c.reply_and_wait(
        sql.Questionnaire.to_pretty_table(quests),
        code_block=True
    )


@a.register(c.command(short.method.list, short.name.subscriber))
@sql.session()
def subscriber(c, session=None):
    subs = (
        session
        .query(sql.Subscriber)
        .order_by(
            sql.Subscriber.active.desc(),
            sql.Subscriber.admin.desc(),
            sql.Subscriber.name.asc()
        )
        .all()
    )
    return c.reply_and_wait(
        sql.Subscriber.to_pretty_table(subs),
        code_block=True
    )


@a.register(c.command(short.method.list, short.name.subscription))
@sql.session()
def subscription(c, session=None):
    try:
        name = c.cs_command_args[2]
        quest = (
            session
            .query(sql.Questionnaire)
            .filter(sql.Questionnaire.name == name)
            .one()
        )
    except orme.NoResultFound:
        return c.reply_and_wait(NO_QUEST_WITH_NAME.format(name))
    except IndexError:
        return c.reply_and_wait(NO_QUEEST_NAME)
    subscr = (
        session
        .query(sql.Subscription)
        .join(sql.Subscriber)
        .filter(sql.Subscription.questionnaire == quest)
        .order_by(
            sql.Subscriber.active.desc(),
            sql.Subscription.active.desc()
        )
        .all()
    )
    return c.reply_and_wait(
        sql.Subscription.to_pretty_table(subscr),
        code_block=True
    )
