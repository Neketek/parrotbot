from modules.model import sql
from sqlalchemy.orm import exc as orme
from modules.controller.core import\
    parsers as p, actions as a, Conditions as c
from ..common import labels as lb, checks as ch
from modules.config.naming import short
from modules.controller import permission
from modules.controller.core import utils
from .help_text import TEXT as HTEXT
from modules.controller.scheduled.report import plan


__QUEST = short.name.questionnaire
__SUB = short.name.subscriber

__CMD = dict()
__CMD[__QUEST] = (
    short.method.set,
    short.name.subscription,
    short.name.questionnaire,
)
__CMD[__SUB] = (
    short.method.set,
    short.name.subscription,
    short.name.questionnaire,
)


def __params(root, names):
    return [
        "{}_name".format(root),
        "param",
        "value",
        "{}_name,...".format(names)
    ]


CMD = dict()
CMD[__QUEST] = utils.cmd_str(*__CMD[__QUEST], params=__params(__QUEST, __SUB))
CMD[__SUB] = utils.cmd_str(*__CMD[__SUB], params=__params(__SUB, __QUEST))

COMMAND = """
`set subscr <quest|subs> <quest_name> <param> <value> <sub_name,...>`
"""

NO_QUEST_NAME = """
Pls, provide quest_name.{}
""".format(CMD[__QUEST])

NO_SUB_NAMES = """
Pls, provide sub name(s).{}
""".format(CMD[__QUEST])

NO_QUEST_NAMES = """
Pls, provide quest name(s).{}
""".format(CMD[__SUB])

NO_SUB_NAME = """
Pls, provide sub_name.{}
""".format(CMD[__SUB])

SUB_NOT_FOUND = """
Subscriber *{}* not found.
"""

QUEST_NOT_FOUND = """
Questionnaire *{}* not found.
"""


def set_subscrs_active(c, session, subscrs, value):
    value = p.Str.bool(value)
    for s in subscrs:
        s.active = value
        session.add(s)
    session.commit()
    plan.update(session)
    return c.reply_and_wait("Done.")


__PARAM_SETTERS = dict(
    active=set_subscrs_active
)


def get_params_and_setter(c, name_error_text, targets_error_text, cmd):
    args = c.command_args[3:]
    cs_args = c.cs_command_args[3:]
    try:
        name = cs_args[0]
    except IndexError:
        raise ValueError(name_error_text)
    try:
        param = args[1]
        func = __PARAM_SETTERS[param]
    except IndexError:
        raise ValueError(lb.no_param(cmd))
    except KeyError:
        raise ValueError(lb.unknown_param(cmd))
    try:
        value = args[2]
    except IndexError:
        raise ValueError(lb.no_value(cmd))
    targets = cs_args[3:]
    if len(targets) == 0:
        raise ValueError(targets_error_text)
    return name, param, value, targets, func


def __get_subs_quest_mode(c, session):
    name, param, value, subs, setter = get_params_and_setter(
        c,
        NO_QUEST_NAME,
        NO_SUB_NAMES,
        CMD[__QUEST]
    )
    try:
        quest = (
            session
            .query(sql.Questionnaire)
            .filter(sql.Questionnaire.name == name)
            .one()
        )
    except orme.NoResultFound:
        raise ValueError(QUEST_NOT_FOUND.format(name))
    subscrs = (
        session
        .query(sql.Subscription)
        .join(sql.Subscriber)
        .filter(sql.Subscription.questionnaire == quest)
        .filter(sql.Subscriber.name.in_(subs))
        .all()
    )
    ch.compare_found_expected(
        subscrs,
        subs,
        lambda s: s.subscriber.name,
        "Subscriber(s):"
    )
    return subscrs, setter, value


def __get_subs_sub_mode(c, session):
    name, param, value, quests, setter = get_params_and_setter(
        c,
        NO_SUB_NAME,
        NO_QUEST_NAMES,
        CMD[__SUB]
    )
    try:
        sub = (
            session
            .query(sql.Subscriber)
            .filter(sql.Subscriber.name == name)
            .one()
        )
    except orme.NoResultFound:
        raise ValueError(SUB_NOT_FOUND.format(name))
    subscrs = (
        session
        .query(sql.Subscription)
        .join(sql.Questionnaire)
        .filter(sql.Subscription.subscriber == sub)
        .filter(sql.Questionnaire.name.in_(quests))
        .all()
    )
    ch.compare_found_expected(
        subscrs,
        quests,
        lambda s: s.quest.name,
        "Questionnaire(s):"
    )
    return subscrs, setter, value


@a.register(
    c.command(
        *__CMD[__SUB],
        cmd_str=CMD[__SUB],
        cmd_help=HTEXT[__SUB]
    )
)
@a.register(
    c.command(
        *__CMD[__QUEST],
        cmd_str=CMD[__QUEST],
        cmd_help=HTEXT[__QUEST]
    )
)
@sql.session()
@permission.admin()
def subscription(c, session=None):
    try:
        if c.command_args[2] == short.name.questionnaire:
            subscrs, setter, value = __get_subs_quest_mode(c, session)
        else:
            subscrs, setter, value = __get_subs_sub_mode(c, session)
        return setter(c, session, subscrs, value)
    except ValueError as e:
        return c.reply_and_wait(str(e))
