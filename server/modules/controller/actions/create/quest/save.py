from modules.model import sql
from sqlalchemy.orm import exc as orme
from .update_subscribers import update_subscribers
from datetime import datetime
import json


UNABLE_TO_FIND_USERS = """
Creation stopped.
Unable to find user(s):
{0}
"""

ERROR = """
Creation Stoped.
Error:
{0}
"""

SUCCESS = """
Questionnaire {0} was succesfuly created.
"""


def create_schedule(data):
    return sql.Schedule(
        start=data['start'],
        end=data['end'],
        time=datetime.strptime(data['time'], "%H:%M").time()
    )


def get_non_existing_subs(session, subs):
    non_existing_subs = []
    for s in subs:
        try:
            session\
                .query(sql.Subscriber)\
                .filter(sql.Subscriber.name == s)\
                .one()
        except orme.NoResultFound:
            non_existing_subs.append(s)
    return non_existing_subs


def __unsafe_save(c, data):
    subs = data['subscribers']
    session = sql.Session()
    if get_non_existing_subs(session, subs):
        update_subscribers(c, session)
        session.commit()
        non_existing_subs = get_non_existing_subs(session, subs)
        if non_existing_subs:
            raise Exception(
                UNABLE_TO_FIND_USERS.format(
                        json.dumps(
                            non_existing_subs,
                            indent=4
                        )
                    )
            )
    questions = data['questions']
    schedule = data['schedule']
    subs = session\
        .query(sql.Subscriber)\
        .filter(sql.Subscriber.name.in_(subs))
    session.add(
        sql.Questionnaire(
            title=data['title'],
            questions=[sql.Question(text=q) for q in questions],
            subscriptions=[
                sql.Subscription(
                    subscriber_id=s.id
                ) for s in subs
            ],
            schedule=[create_schedule(s) for s in schedule]
        )
    )
    session.commit()
    session.close()


def save(c, data):
    try:
        __unsafe_save(c, data)
        c.reply(SUCCESS.format(data['title']))
    except ValueError as e:
        c.reply(ERROR.format(e))
