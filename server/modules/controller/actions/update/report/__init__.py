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

SUCCESS = """
There are {} pending reports.
"""


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


NEXT_REPORT = """
Report "{}". Starting...
"""


def create_reports_data(c, session=None, reports=None, tz=None):
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
    return dict(
            id=id,
            title=quest.title,
            next=-1,
            questions=questions,
            answers=[],
            tz=tz,
            reports=reports
        )


def save(c, session, data):
    id = data['id']
    questions = data['questions']
    answers = data['answers']
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
    c.reply('Saved!')


def next_question(c, session, data):
    if data['next'] + 1 >= len(data['questions']):
        save(c, session, data)
        if data['reports']:
            return next_question(
                c,
                session,
                create_reports_data(c, session, data['reports'], data['tz'])
            )
        else:
            c.reply("That's all folks :)")
    if data['next'] > 0:
        data['answers'].append(c.text)
    data['next'] += 1
    c.reply("{}) {}".format(
        data['next']+1,
        data['questions'][data['next']]['text'])
    )
    return data


@a.register(c.command('update', 'report'))
@sql.session()
def report(c, session=None):
    if c.next is None:
        pending = get_pending_reports(c.user, session)
        if not pending['ids']:
            c.reply(NO_REPORTS)
            return
        return next_question(
            c,
            session,
            create_reports_data(c, session, pending['ids'], pending['tz'])
        )
    else:
        return next_question(c, session, c.next)
