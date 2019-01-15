from modules.model import sql
from modules.controller.core import\
    parsers as p, actions as a, Conditions as c
from ..common import labels as lb, checks as ch
from modules.config.naming import short
from modules.controller import permission
from modules.controller.core import utils

__CMD = (short.method.set, short.name.subscriber,)
CMD = utils.cmd_str(*__CMD, params=['param', 'value', 'name,...'])


def get_subs_by_name(session, names):
    subs = (
        session
        .query(sql.Subscriber)
        .filter(sql.Subscriber.name.in_(names))
        .all()
    )
    ch.compare_found_expected(
        subs,
        names,
        lambda s: s.name,
        "Subscriber(s):"
    )
    return subs


def set_subs_active(c, session, names, value):
    value = p.Str.bool(value)
    subs = get_subs_by_name(session, names)
    for s in subs:
        s.active = value
        session.add(s)
    session.commit()
    return c.reply_and_wait("Done.")


def set_subs_bot_active(c, session, names, value):
    value = p.Str.bool(value)
    subs = get_subs_by_name(session, names)
    for s in subs:
        s.bot_admin = value
        session.add(s)
    session.commit()
    return c.reply_and_wait("Done.")


@a.register(c.command(*__CMD))
@sql.session()
@permission.admin()
def subscriber(c, session=None):
    args = c.command_args[2:]
    cs_args = c.cs_command_args[2:]
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
            return set_subs_active(c, session, names, value)
        if param == 'bot_admin':
            return set_subs_bot_active(c, session, names, value)
        else:
            return c.reply_and_wait(lb.unknown_param_name(CMD))
    except ValueError as e:
        return c.reply_and_wait(str(e))
