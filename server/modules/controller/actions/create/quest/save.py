from modules.model import sql
from sqlalchemy.orm import exc as orme
from modules.controller.actions.update.subscribers import update_subscribers
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

SEARCHING_FOR_SUBSCRIBERS = """
Need to update subscribers cache for:
{0}
Wait a bit...
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
    try:
        session\
            .query(sql.Questionnaire)\
            .filter(sql.Questionnaire.title == data['title'])\
            .one()
        raise ValueError(
            "Questionnaire {} already exists.".format(data['title'])
        )
    except orme.NoResultFound:
        pass
    non_existing_subs = get_non_existing_subs(session, subs)
    if non_existing_subs:
        c.reply(
            SEARCHING_FOR_SUBSCRIBERS.format(
                "\n\t".join(non_existing_subs)
            )
        )
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
    c.reply('Creation confirmed. Writing to db...')
    try:
        __unsafe_save(c, data)
        c.reply(SUCCESS.format(data['title']))
    except ValueError as e:
        c.reply(ERROR.format(e))
