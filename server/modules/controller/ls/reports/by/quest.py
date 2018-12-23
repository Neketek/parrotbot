from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from sqlalchemy import and_
from modules.controller.core.time import get_shifted_date
from pytz import timezone
from ..common import reply_msg_attachments, get_channel_sub
from ..commont_text import no_days_range, days_range_is_not_int, no_names


COMMAND_TEMPLATE = "`ls reports quest <days> <name,...>`"


NO_QUEST_NAME = """
Pls, provide quest name(s).
{}
""".format(COMMAND_TEMPLATE)

NO_QUEST_WITH_NAME = """
No quest with name(s):
{}
"""


def NO_QUEST_WITH_NAMEs(titles):
    return no_names(NO_QUEST_WITH_NAME, titles)


@a.register(c.command('ls', 'reports', 'quest'))
@sql.session()
def quest(c, session=None):
    args = c.command_args
    cs_args = c.cs_command_args
    if len(args) < 5:
        if len(args) < 4:
            c.reply(no_days_range)
            return
        c.reply(NO_QUEST_NAME)
        return
    try:
        days = int(args[3])
    except ValueError:
        c.reply(days_range_is_not_int(COMMAND_TEMPLATE))
    names = cs_args[4:]
    try:
        sub = get_channel_sub(c, session)
    except ValueError as e:
        c.reply(e)
        return
    quests = (
        session
        .query(sql.Questionnaire)
        .filter(sql.Questionnaire.name.in_(names))
        .all()
    )
    if len(quests) < len(names):
        found = [q.name for q in quests]
        not_found = [n for n in names if n not in found]
        c.reply(NO_QUEST_WITH_NAMEs(not_found))
        return
    tz = timezone(sub.tz)
    date_boundary = get_shifted_date(tz, -days)
    reports = (
        session
        .query(
            sql.Report,
            sql.Subscriber,
            sql.Questionnaire
        )
        .join(
            sql.Subscription,
            and_(
                sql.Subscription.active,
                sql.Report.created >= date_boundary,
                sql.Subscription.id == sql.Report.subscription_id
            )
        )
        .join(
            sql.Questionnaire,
            and_(
                sql.Questionnaire.name.in_(names),
                sql.Subscription.questionnaire_id == sql.Questionnaire.id
            )
        )
        .join(sql.Subscriber)
        .order_by(
            sql.Questionnaire.title.asc(),
            sql.Subscriber.tz.asc(),
            sql.Subscriber.name.asc(),
            sql.Report.created.desc()
        )
        .all()
    )
    return reply_msg_attachments(
        c,
        session,
        None,
        reports
    )
