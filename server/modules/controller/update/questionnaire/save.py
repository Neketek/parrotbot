from modules.model import sql
from sqlalchemy.orm import exc as orme
from datetime import datetime


def save(c, session):
    data = c.i.next
    name = data['name']
    try:
        quest = (
            session
            .query(sql.Questionnaire)
            .filter(sql.Questionnaire.name == name)
            .one()
        )
    except orme.NoResultFound:
        raise ValueError("Can't find questionnaire *{}*".format(name))
    try:
        title = data['title']
        quest.title = title
    except KeyError:
        pass
    try:
        sub_names = data['subscribers']
        subs = (
            session
            .query(sql.Subscriber)
            .join(sql.Subscription)
            .filter(sql.Subscriber.name.in_(sub_names))
            .filter(sql.Subscription.questionnaire != quest)
        )
        for s in subs:
            quest.subscriptions.add(
                sql.Subscription(
                    subscriber=s,
                    questionnaire=quest
                )
            )
        subscr_to_delete = (
            session
            .query(sql.Subscription.id)
            .join(sql.Subscriber)
            .filter(sql.Subscription.questionnaire == quest)
            .filter(sql.Subscriber.name.notin_(sub_names))
        )
        (
            session
            .query(sql.Subscription)
            .filter(sql.Subscription.id.in_(subscr_to_delete.subquery()))
            .delete(synchronize_session=False)
        )
    except KeyError:
        pass
    try:
        schedule = data['schedule']
        quest.schedule = [
            sql.Schedule(
                start=sch['start'],
                end=sch['end'],
                time=datetime.time.strftime(sch['time'], "%H:%M")
            )
            for sch in schedule
        ]
    except KeyError:
        pass
    try:
        quest.expiration = data['expiration']
    except KeyError:
        pass
    try:
        quest.retention = data['retention']
    except KeyError:
        pass
    session.add(quest)
    session.commit()
    return c.reply_and_wait('Done.')
