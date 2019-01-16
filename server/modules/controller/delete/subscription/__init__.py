from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from modules.controller.set.common.checks import compare_found_expected
from modules.config.naming import short
from sqlalchemy.orm import exc as orme
from modules.controller import permission
from modules.controller.core import utils
from .help_text import TEXT as HTEXT
from modules.controller.scheduled.report import plan

__CMD = (short.method.delete, short.name.subscription,)
__PARAMS = [
    "{}_name".format(short.name.questionnaire),
    "{}_name".format(short.name.subscriber)
]
CMD = utils.cmd_str(*__CMD, params=__PARAMS)

NO_QUEST_NAME = """
Pls, provide questionnaire name.
{}
""".format(CMD)

NO_QUEST_WITH_NAME = """
Questionnaire {} not found.
"""

NO_SUB_NAMES = """
Pls, provide subscriber names(s).
{}
""".format(CMD)


@a.register(c.command(*__CMD, cmd_str=CMD, cmd_help=HTEXT))
@sql.session()
@permission.admin()
def subscription(c, session=None):
    cs_args = c.command_args[2:]
    try:
        quest_name = cs_args[0]
    except IndexError:
        return c.reply_and_wait(NO_QUEST_NAME)
    try:
        quest = (
            session
            .query(sql.Questionnaire)
            .filter(sql.Questionnaire.id)
            .one()
        )
    except orme.NoResultFound:
        raise c.reply_and_wait(
            NO_QUEST_WITH_NAME.format(quest_name)
        )
    sub_names = cs_args[1:]
    if len(sub_names) == 0:
        return c.reply_and_wait(NO_SUB_NAMES)
    subscrs_query = (
        session
        .query(sql.Subscription)
        .join(sql.Subscriber)
        .filter(sql.Subscription.questionnaire == quest)
        .filter(sql.Subscriber.name.in_(sub_names))
    )
    subscrs = subscrs_query.all()
    try:
        compare_found_expected(
            subscrs,
            sub_names,
            lambda s: s.subscriber.name,
            "Subscriber(s):"
        )
    except ValueError as e:
        return c.reply_and_wait(e)
    for s in subscrs:
        session.delete(s)
    session.commit()
    plan.update(session)
    return c.reply_and_wait(
        "Done. {} subscription(s) removed from {} questionnaire"
        .format(len(sub_names), quest_name)
    )
