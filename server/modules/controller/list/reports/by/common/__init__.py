from modules.model import sql
from sqlalchemy import and_
from pytz import timezone
from modules.controller.core.time import get_now
from sqlalchemy.orm import exc as orme

NOT_SUBSCRIBER = """
You're not a subscriber. Can't get your timezone.
Pls, update subscribers.
"""


def get_channel_sub(c, session):
    try:
        return (
            session
            .query(sql.Subscriber)
            .filter(sql.Subscriber.id == c.user)
            .one()
        )
    except orme.NoResultFound:
        raise ValueError(NOT_SUBSCRIBER)


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


QA_HEADER = """
{user} {created}->{completed}
"""

QA_HEADER_WITH_TITLE = """
{{title}}
{}
""".format(QA_HEADER)

QA_FORMAT = """
Q({0}):{1}
A({0}):{2}
"""

PENDING = "PENDING"
OVERDUE = "OVERDUE"


def datetime_str(date):
    return date.strftime("%m-%d %H:%m")


def completed_datetime_str(report, sub):
    if report.completed is not None:
        return datetime_str(report.completed)
    else:
        tz = timezone(sub.tz)
        now = get_now(tz)
        exp = tz.localize(report.expiration)
        return PENDING if exp > now else OVERDUE


def report_to_header_vars(quest, report, sub):
    return dict(
        title=quest.title,
        user=sub.name,
        uid=sub.id,
        created=datetime_str(report.created),
        completed=completed_datetime_str(report, sub),
        tz=sub.tz
    )


def report_to_qa_vars(session, quest, report):
    qa = get_qa(session, quest, report)
    qa_vars = []
    n = 1
    for q, a in qa:
        qa_vars.append(("{}. {}".format(n, q.text), a.text,))
        n += 1
    return qa_vars


COLOR_WARN = "warning"
COLOR_DANGER = "danger"
COLOR_GOOD = "good"


def get_color_from_status(status):
    if status == PENDING:
        return COLOR_WARN
    elif status == OVERDUE:
        return COLOR_DANGER
    else:
        return COLOR_GOOD


def report_to_msg_attachment(session, quest, report, sub):
    header = report_to_header_vars(quest, report, sub)
    qa = report_to_qa_vars(session, quest, report)
    attachment = dict(
        color=get_color_from_status(header['completed']),
        fields=[
            dict(
                title=q,
                value=a
            )
            for
            q, a in qa
        ],
        footer="*id: {}*".format(report.id),
        pretext="*<@{}> {} {}->{} {}*".format(
            header['uid'],
            header['title'],
            header['created'],
            header['completed'],
            header['tz']
        )
    )
    if not qa:
        attachment['text'] = 'No data'
    return attachment


def reports_to_msg_attachments(session, quest, query):
    attachments = []
    if quest is None:
        for r, s, q in query:
            attachments.append(
                report_to_msg_attachment(
                    session,
                    q,
                    r,
                    s
                )
            )
    else:
        for r, s in query:
            attachments.append(
                report_to_msg_attachment(
                    session,
                    quest,
                    r,
                    s
                )
            )
    return attachments


def chunk_generator(l, size):
    for i in range(0, len(l), size):
        yield l[i:i+size]


CHUNK_SIZE = 20


def reply_msg_attachments(c, session, quest, query):
    page = 1
    last_msg = None
    for ch in chunk_generator(query, CHUNK_SIZE):
        last_msg = c.reply(
            "*`Page:{}`*".format(page),
            attachments=reports_to_msg_attachments(
                session,
                quest,
                ch
            )
        )
        page += 1
    if last_msg is not None:
        return c.result().wait(last_msg.get('message'))
