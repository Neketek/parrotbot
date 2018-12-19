from modules.model import sql
from modules.controller.core import actions as a, Conditions as c
from modules.controller.core.time import get_now
from sqlalchemy import and_
from sqlalchemy.orm import exc as orme
from pytz import timezone


NO_REPORTS = """
You have no pending reports.
"""

NOT_SUBSCRIBER = '''
You are not a subscriber!
There is no record about you.
'''


def get_pending_reports(user_id, session):
    try:
        sub = (
            session
            .query(sql.Subscriber)
            .filter(sql.Subscriber.id == user_id)
            .one()
        )
        tz = timezone(sub.tz)
        now = get_now(tz)
    except orme.NoResultFound:
        raise ValueError(NOT_SUBSCRIBER)
    reports = (
        session
        .query(sql.Report)
        .join(
            sql.Subscription,
            and_(
                sql.Subscription.subscriber_id == sub.id,
                sql.Subscription.id == sql.Report.subscription_id,
                sql.Subscription.active
            )
        ).filter(
            sql.Report.completed.is_(None),
            sql.Report.expiration > now
        )
        .order_by(sql.Report.expiration.asc())
        .all()
    )
    return dict(ids=[r.id for r in reports], tz=tz)


STOP_COMMAND = ".stop"

REPORTING_STOPPED = """
Report stopped. You can start it again using `report` command.
"""

NEXT_REPORT = """
Starting report "{}"...
"""

PENDING_REPORTS_FETCHED = """
There are {{}} pending reports. To stop reporting type `{}`
{{{{}}}}
""".format(STOP_COMMAND)

PENDING_REPORTS_LEFT = """
There are {} pending reports left.
{{}}
"""


def create_report_state_data(c, session=None, reports=None, tz=None):
    if c.next is None:
        msg = PENDING_REPORTS_FETCHED.format(len(reports))
    else:
        msg = PENDING_REPORTS_LEFT.format(len(reports))
    reports = list(reports)
    id = reports.pop(0)
    quest = (
        session
        .query(sql.Questionnaire)
        .join(sql.Subscription)
        .join(sql.Report)
        .filter(sql.Report.id == id)
        .one()
    )
    questions = [
        dict(id=q.id, text=q.text)
        for
        q in (
            session
            .query(sql.Question)
            .filter(sql.Question.questionnaire_id == quest.id)
            .all()
        )
    ]
    c.reply(msg.format(NEXT_REPORT.format(quest.title)))
    return dict(
            id=id,
            title=quest.title,
            next=-1,
            questions=questions,
            answers=[],
            tz=tz,
            reports=reports
        )


REPORT_SAVED = """
Report successfully saved!
"""


def save(c, session, data):
    id = data['id']
    questions = data['questions']
    answers = data['answers']
    # print("ANSWERS", answers)
    for i in range(len(data['answers'])):
        session.add(
            sql.Answer(
                report_id=id,
                question_id=questions[i]['id'],
                text=answers[i]
            )
        )
    (
        session
        .query(sql.Report)
        .filter(sql.Report.id == id)
        .update({sql.Report.completed: get_now(data['tz'])})
    )
    session.commit()
    c.reply(REPORT_SAVED)


ALL_REPORTS_COMPLETED = """
You completed all pending reports. See you soon.
"""


ANSWER_IS_TOO_LONG = """
Answer is too long. Try to be laconic.
Limit is {} chars.
"""


def check_answer_length(answer):
    max_length = sql.Answer.text.property.columns[0].type.length
    if len(answer) > max_length:
        raise ValueError(ANSWER_IS_TOO_LONG.format(max_length))


def next_question(c, session, data):
    if c.command == STOP_COMMAND:
        c.reply(REPORTING_STOPPED)
        return
    if data['next'] >= 0:
        max_length = sql.Answer.text.property.columns[0].type.length
        if len(c.text) > max_length:
            c.reply(ANSWER_IS_TOO_LONG.format(max_length))
            return data
        data['answers'].append(c.text)
    if data['next'] + 1 >= len(data['questions']):
        save(c, session, data)
        if data['reports']:
            return next_question(
                c,
                session,
                create_report_state_data(
                    c,
                    session,
                    data['reports'],
                    data['tz']
                )
            )
        else:
            c.reply(ALL_REPORTS_COMPLETED)
            return
    data['next'] += 1
    c.reply("{}) {}".format(
        data['next']+1,
        data['questions'][data['next']]['text'])
    )
    return data


@a.register(c.command('update', 'report'))
@sql.session()
def report(c, session=None):
    try:
        if c.next is None:
            pending = get_pending_reports(c.user, session)
            if not pending['ids']:
                c.reply(NO_REPORTS)
                return
            return next_question(
                c,
                session,
                create_report_state_data(
                    c,
                    session,
                    pending['ids'],
                    pending['tz']
                )
            )
        else:
            return next_question(c, session, c.next)
    except ValueError as e:
        c.reply(e)
        return
