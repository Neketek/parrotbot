from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from sqlalchemy import and_
from modules.controller.core.time import get_shifted_date
from pytz import timezone
from .common import reply_msg_attachments, get_channel_sub
from .common.labels import no_days_range, days_range_is_not_int, no_names
from modules.config.naming import short
from modules.controller import permission

COMMAND = "`ls reports quest <days> <name,...>`"


NO_QUEST_NAME = """
Pls, provide questionnaire name(s).
{}
""".format(COMMAND)

NO_QUEST_WITH_NAME = """
Questionnaire(s) not found:
{}
"""


def no_quest_with_name(titles):
    return no_names(NO_QUEST_WITH_NAME, titles)


@a.register(
    c.command(
        short.method.list,
        short.name.report,
        short.name.questionnaire
    )
)
@sql.session()
@permission.admin()
def quest(c, session=None):
    args = c.command_args
    cs_args = c.cs_command_args
    if len(args) < 5:
        if len(args) < 4:
            return c.reply_and_wait(no_days_range(COMMAND))
        return c.reply_and_wait(NO_QUEST_NAME)
    try:
        days = int(args[3])
    except ValueError:
        return c.reply_and_wait(days_range_is_not_int(COMMAND))
    names = cs_args[4:]
    try:
        sub = get_channel_sub(c, session)
    except ValueError as e:
        return c.reply_and_wait(e)
    quests = (
        session
        .query(sql.Questionnaire)
        .filter(sql.Questionnaire.name.in_(names))
        .all()
    )
    if len(quests) < len(names):
        found = [q.name for q in quests]
        not_found = [n for n in names if n not in found]
        return c.reply_and_wait(no_quest_with_name(not_found))
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
