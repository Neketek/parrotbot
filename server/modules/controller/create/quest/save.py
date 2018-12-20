from modules.model import sql
from sqlalchemy.orm import exc as orme
from datetime import datetime
import json


UNABLE_TO_FIND_USERS = """
Unable to find user(s):
{0}
Try to update subscribers.
"""

SUCCESS = """
Questionnaire {0} was succesfuly created.
"""


def time_from_str(value):
    if value is None:
        return None
    return datetime.strptime(value, "%H:%M").time()


def create_schedule(data):
    return sql.Schedule(
        start=data['start'],
        end=data['end'],
        time=time_from_str(data['time'])
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


def __unsafe_save(c, session, data):
    subs = data['subscribers']
    try:
        session\
            .query(sql.Questionnaire)\
            .filter(sql.Questionnaire.name == data['name'])\
            .one()
        raise ValueError(
            "Questionnaire name: {} already exists.".format(data['name'])
        )
    except orme.NoResultFound:
        pass
    non_existing_subs = get_non_existing_subs(session, subs)
    if non_existing_subs:
            raise ValueError(
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
            name=data['name'],
            title=data['title'],
            questions=[sql.Question(text=q) for q in questions],
            expiration=time_from_str(data.get('expiration')),
            subscriptions=[
                sql.Subscription(
                    subscriber_id=s.id
                ) for s in subs
            ],
            schedule=[create_schedule(s) for s in schedule]
        )
    )
    session.commit()


@sql.session()
def save(c, data, session=None):
    c.reply("Saving questionnaire to db...")
    __unsafe_save(c, session, data)
    c.reply(SUCCESS.format(data['title']))
    return
