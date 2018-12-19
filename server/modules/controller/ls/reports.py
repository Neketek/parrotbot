from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from sqlalchemy.orm import exc as orme
from sqlalchemy import and_
from modules.controller.core.time import get_shifted_date
from pytz import timezone


def get_qa(session, quest, report):
    if report.completed is None:
        return []
    return (
        session
        .query(
            sql.Question,
            sql.Answer
        ).join(
            sql.Answer,
            and_(
                sql.Question.questionnaire_id == quest.id,
                sql.Answer.report_id == report.id,
                sql.Answer.question_id == sql.Question.id
            )
        )
        .order_by(
            sql.Question.id.asc()
        )
        .all()
    )


QA_FORMAT = """
Q({0}):{1}
A({0}):{2}
"""


def report_to_msg(session, quest, report, sub):
    qa = get_qa(session, quest, report)
    result = "user:{} created:{} completed:{}\n".format(
        sub.display_name if len(sub.display_name) > 0 else sub.name,
        report.created.strftime("%m-%d %H:%m"),
        None if report.completed is None else report.completed.strftime("%m-%d %H:%m")
    )
    n = 1
    for q, a in qa:
        result += QA_FORMAT.format(n, q.text, a.text)
        n += 1
    return result


def reports_to_msg(session, quest, query):
    msg = ""
    for r, s in query:
        msg += "{}\n".format(
            report_to_msg(
                session,
                quest,
                r,
                s
            )
        )
    return msg


NO_DAYS_RANGE = """
Pls, provide days range.
`ls reports quest <title> <days>`
"""

NO_QUEST_NAME = """
Pls, provide quest title.
`ls reports quest <title> <days>`
"""


DAYS_RANGE_IS_NOT_INT = """
<days> should be int.
`ls reports quest <title> <days>`
"""

NO_QUEST = """
Can't find quest "{}"
"""

NOT_SUBSCRIBER = """
You're not a subscriber. Can't get your timezone.
Pls, update subscribers.
"""


@a.register(c.command('ls', 'reports', 'quest'))
@sql.session()
def ls_reports(c, session=None):

    args = c.command_args
    cs_args = c.cs_command_args

    if len(args) < 4:
        c.reply(NO_QUEST_NAME)
        return
    if len(args) < 5:
        c.reply(NO_DAYS_RANGE)
        return
    title = cs_args[3]
    days = args[4]
    try:
        days = int(days)
    except ValueError:
        c.reply(DAYS_RANGE_IS_NOT_INT)
        return
    try:
        sub = (
            session
            .query(sql.Subscriber)
            .filter(sql.Subscriber.id == c.user)
            .one()
        )
    except orme.NoResultFound:
        c.reply(NOT_SUBSCRIBER)
        return
    try:
        quest = (
            session
            .query(sql.Questionnaire)
            .filter(sql.Questionnaire.title == title)
            .one()
        )
    except orme.NoResultFound:
        c.reply(NO_QUEST.format(c.command_args[3]))
        return
    tz = timezone(sub.tz)
    days_shift = get_shifted_date(tz, -days)
    reports = (
        session
        .query(
            sql.Report,
            sql.Subscriber
        )
        .join(sql.Subscription)
        .join(sql.Subscriber)
        .filter(
            and_(
                sql.Report.created >= days_shift,
                sql.Subscription.questionnaire_id == quest.id
            )
        )
        .order_by(
            sql.Subscriber.tz.asc(),
            sql.Subscriber.id.asc(),
            sql.Report.created.asc(),
            sql.Report.completed.asc()
        )
        .all()
    )
    c.reply(reports_to_msg(session, quest, reports))
