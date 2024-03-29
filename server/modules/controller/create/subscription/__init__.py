from modules.controller.set.common.checks import compare_found_expected
from modules.controller.core import actions as a, Conditions as c
from modules.config.naming import short
from sqlalchemy.orm import exc as orme
from modules.model import sql
from modules.controller.core import utils
from .help_text import TEXT as HTEXT
from modules.controller.scheduled.report import plan

__CMD = (short.method.create, short.name.subscription,)
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
Pls, provide subscriber name(s).
{}
""".format(CMD)


@a.register(c.command(*__CMD, cmd_str=CMD, cmd_help=HTEXT))
@sql.session()
def subscription(c, session=None):
    cs_args = c.cs_command_args[2:]
    try:
        quest_name = cs_args[0]
    except IndexError:
        return c.reply_and_wait(NO_QUEST_NAME)
    try:
        quest = (
            session
            .query(sql.Questionnaire)
            .filter(sql.Questionnaire.name == quest_name)
            .one()
        )
    except orme.NoResultFound:
        return c.reply_and_wait(
            NO_QUEST_WITH_NAME.format(quest_name)
        )
    sub_names = cs_args[1:]
    if len(sub_names) == 0:
        return c.reply_and_wait(NO_SUB_NAMES)
    subs = (
        session
        .query(sql.Subscriber)
        .filter(sql.Subscriber.name.in_(sub_names))
        .all()
    )
    try:
        compare_found_expected(
            subs,
            sub_names,
            lambda s: s.name,
            "Subscriber(s):"
        )
    except ValueError as e:
        return c.reply_and_wait(e)
    existing = (
        session
        .query(sql.Subscriber)
        .join(sql.Subscription)
        .filter(sql.Subscription.questionnaire == quest)
        .filter(sql.Subscriber.name.in_(sub_names))
        .all()
    )
    non_existing = [s for s in subs if s not in existing]
    for s in non_existing:
        session.add(
            sql.Subscription(
                subscriber=s,
                questionnaire=quest
            )
        )
    session.commit()
    plan.update(session)
    return c.reply_and_wait(
        "Done. Added {} new subscription(s). {} already exist(s)"
        .format(len(non_existing), len(existing))
    )
