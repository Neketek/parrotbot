from modules.controller.core import actions as a, Conditions as c
from modules.config.naming import short
from modules.model import sql
from sqlalchemy.orm import exc as orme
from modules.controller import permission
from modules.controller.core import utils
from .help_text import TEXT as HTEXT
from . import reports
from modules.controller.scheduled.report import plan as rplan
import json


NO_QUEEST_NAME = """
Pls, provide questionnaire name.
"""

NO_QUEST_WITH_NAME = """
Can't find questionnaire *{0}*.
"""

__CMD = dict()
CMD = dict()
__CMD[short.name.question] = (short.method.list, short.name.question, )
CMD[short.name.question] = utils.cmd_str(*__CMD[short.name.question])


@a.register(
    c.command(
        *__CMD[short.name.question],
        cmd_str=CMD[short.name.question],
        cmd_help=HTEXT[short.name.question]
    )
)
@sql.session()
@permission.admin()
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


__CMD[short.name.questionnaire] = (
    short.method.list,
    short.name.questionnaire,
)
CMD[short.name.questionnaire] = utils.cmd_str(*__CMD[short.name.questionnaire])


@a.register(
    c.command(
        *__CMD[short.name.questionnaire],
        cmd_str=CMD[short.name.questionnaire],
        cmd_help=HTEXT[short.name.questionnaire]
    )
)
@sql.session()
@permission.admin()
def questionnaire(c, session=None):
    quests = session\
        .query(sql.Questionnaire)\
        .order_by(sql.Questionnaire.id.asc())\
        .all()
    return c.reply_and_wait(
        sql.Questionnaire.to_pretty_table(quests),
        code_block=True
    )


__CMD[short.name.subscriber] = (short.method.list, short.name.subscriber, )
CMD[short.name.subscriber] = utils.cmd_str(*__CMD[short.name.subscriber])


@a.register(
    c.command(
        *__CMD[short.name.subscriber],
        cmd_str=CMD[short.name.subscriber],
        cmd_help=HTEXT[short.name.subscriber]
    )
)
@sql.session()
@permission.admin()
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


__CMD[short.name.subscription] = (short.method.list, short.name.subscription, )
CMD[short.name.subscription] = utils.cmd_str(
    *__CMD[short.name.subscription],
    params=[
        "{}_name".format(short.name.questionnaire)
    ]
)


@a.register(
    c.command(
        *__CMD[short.name.subscription],
        cmd_str=CMD[short.name.subscription],
        cmd_help=HTEXT[short.name.subscription]
    )
)
@sql.session()
@permission.admin()
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


__CMD[short.name.schedule] = (short.method.list, short.name.schedule, )
CMD[short.name.schedule] = utils.cmd_str(*__CMD[short.name.schedule])


@a.register(
    c.command(
        *__CMD[short.name.schedule],
        cmd_str=CMD[short.name.schedule],
        cmd_help=HTEXT[short.name.schedule]
    )
)
@sql.session()
@permission.admin()
def schedule(c, session=None):
    try:
        name = c.cs_command_args[2]
    except IndexError:
        return c.reply_and_wait(NO_QUEEST_NAME)
    try:
        quest = (
            session
            .query(sql.Questionnaire)
            .filter(sql.Questionnaire.name == name)
            .one()
        )
    except orme.NoResultFound:
        return c.reply_and_wait(NO_QUEST_WITH_NAME.format(name))
    return c.reply_and_wait(
        str(sql.Schedule.to_pretty_table(quest.schedule)),
        code_block=True
    )


__CMD[short.name.plan] = (short.method.list, short.name.plan, )
CMD[short.name.plan] = utils.cmd_str(*__CMD[short.name.plan])

# Has a problem with file upload, bot 'thinks' that file upload event source
# is other user because it contains bot user id
# @a.register(
#     c.command(
#         *__CMD[short.name.plan],
#         cmd_str=CMD[short.name.plan],
#         cmd_help=HTEXT[short.name.plan]
#     )
# )
# @sql.session()
# @permission.admin()
# def plan(c, session=None):
#     try:
#         data = rplan.load()
#     except FileNotFoundError:
#         plan.create()
#         data = rplan.update(session)
#     return c.upload_file(
#         c.channel,
#         json.dumps(data, indent=4),
#         "plan.json",
#         "json"
#     )
