from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from sqlalchemy import and_
from modules.controller.core.time import get_shifted_date
from pytz import timezone
from .common import reply_msg_attachments, get_channel_sub
from .common.labels import no_days_range, days_range_is_not_int, no_names
from modules.config.naming import short


COMMAND = "`{} {} {} <{}> <{},...>`".format(
    short.method.ls,
    short.name.report,
    short.name.subscriber,
    short.param.days,
    'subscriber'
)

NO_SUB_NAMES = """
Pls, provide sub name(s)
{}
""".format(COMMAND)

NO_SUBS_WITH_NAME = """
No subs with name(s):
{}
"""


def no_subs_with_name(names):
    return no_names(NO_SUBS_WITH_NAME, names)


@a.register(
    c.command(
        short.method.list,
        short.name.report,
        short.name.subscriber
    )
)
@sql.session()
def subscriber(c, session=None):
    args = c.command_args
    cs_args = c.cs_command_args
    if len(args) < 4:
        return c.reply_and_wait(no_days_range(COMMAND))
    if len(args) < 5:
        return c.reply_and_wait(NO_SUB_NAMES)
    try:
        days = int(c.command_args[3])
    except ValueError:
        return c.reply_and_wait(days_range_is_not_int(COMMAND))
    try:
        sub = get_channel_sub(c, session)
    except ValueError as e:
        return c.reply_and_wait(e)
    names = cs_args[4:]
    subs = (
        session
        .query(sql.Subscriber)
        .filter(sql.Subscriber.name.in_(names))
        .all()
    )
    if len(subs) < len(names):
        found = [s.name for s in subs]
        not_found = [n for n in names if n not in found]
        return c.reply_and_wait(no_subs_with_name(not_found))
    sub_ids = [s.id for s in subs]
    tz = timezone(sub.tz)
    date_boundary = get_shifted_date(tz, -days)
    reports = (
        session
        .query(
            sql.Report,
            sql.Subscriber,
            sql.Questionnaire
        ).join(
            sql.Subscription,
            and_(
                sql.Subscription.active,
                sql.Report.created >= date_boundary,
                sql.Subscription.subscriber_id.in_(sub_ids),
                sql.Report.subscription_id == sql.Subscription.id
            )
        )
        .join(sql.Questionnaire)
        .join(sql.Subscriber)
        .order_by(
            sql.Subscriber.id,
            sql.Report.created.desc()
        ).all()
    )
    return reply_msg_attachments(c, session, None, reports)
