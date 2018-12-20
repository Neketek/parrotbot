from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from sqlalchemy.orm import exc as orme
from sqlalchemy import and_
from modules.controller.core.time import get_shifted_date
from pytz import timezone
from ..common import reply_msg_attachments, get_channel_sub
from ..commont_text import no_days_range, days_range_is_not_int, no_names


COMMAND_TEMPLATE = "`ls reports sub <days> <sub,...>`"

NO_SUB_NAMES = """
Pls, provide sub name(s)
{}
""".format(COMMAND_TEMPLATE)

NO_SUBS_WITH_NAME = """
No subs with name(s):
{}
"""


def no_subs_with_name(names):
    return no_names(NO_SUBS_WITH_NAME, names)


@a.register(c.command('ls', 'reports', 'sub'))
@sql.session()
def subscriber(c, session=None):
    args = c.command_args
    cs_args = c.cs_command_args
    if len(args) < 4:
        c.reply(no_days_range(COMMAND_TEMPLATE))
        return
    if len(args) < 5:
        c.reply(NO_SUB_NAMES)
        return
    try:
        days = int(c.command_args[3])
    except ValueError:
        c.reply(days_range_is_not_int(COMMAND_TEMPLATE))
        return
    try:
        sub = get_channel_sub(c, session)
    except ValueError as e:
        c.reply(e)
        return
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
        c.reply(no_subs_with_name(not_found))
        return
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
    reply_msg_attachments(c, session, None, reports)
