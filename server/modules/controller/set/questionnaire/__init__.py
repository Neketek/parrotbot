from modules.controller.core import\
    actions as a, Conditions as c, parsers as p
from modules.model import sql
from ..common import labels as lb, checks as ch
# from sqlalchemy.orm import exc as orme
from modules.config.naming import short
from modules.controller import permission
from modules.controller.core import utils

__CMD = (short.method.set, short.name.questionnaire,)
CMD = utils.cmd_str(*__CMD, params=['param', 'value', 'name,...'])


def get_quest_by_name(session, names):
        quests = (
            session
            .query(sql.Questionnaire)
            .filter(sql.Questionnaire.name.in_(names))
            .all()
        )
        ch.compare_found_expected(
            quests,
            names,
            lambda q: q.name,
            "Questionnaire(s):"
        )
        return quests


def set_quest_active(c, session, names, value):
    quests = get_quest_by_name(session, names)
    value = p.Str.bool(value)
    for q in quests:
        q.active = value
        session.add(q)
    session.commit()
    return c.reply_and_wait("Done.")


@a.register(c.command(*__CMD))
@sql.session()
@permission.admin()
def questionnaire(c, session=None):
    cs_args = c.cs_command_args[2:]
    args = c.command_args[2:]
    try:
        param = args[0]
    except IndexError:
        return c.reply_and_wait(lb.no_param(CMD))
    try:
        value = args[1]
    except IndexError:
        return c.reply_and_wait(lb.no_value(CMD))
    names = cs_args[2:]
    if len(names) == 0:
        return c.reply_and_wait(lb.no_name(CMD))
    try:
        if param == 'active':
            set_quest_active(c, session, names, value)
        else:
            return c.reply_and_wait(lb.unknown_param_name(CMD))
    except ValueError as e:
        return c.reply_and_wait(str(e))
