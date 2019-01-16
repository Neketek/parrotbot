from modules.model import sql
from sqlalchemy import not_
import json
from .constant import TIME_FORMAT

FILENAME = "plan.json"


def __get_or_create(s, k, d):
    try:
        return s[k]
    except KeyError:
        s[k] = d
        return d


def __get_subs(session):
    subs_data = dict()
    subs = (
        session
        .query(sql.Subscriber)
        .filter(sql.Subscriber.active)
        .filter(not_(sql.Subscriber.archived))
        .all()
    )
    for sub in subs:
        subs_data[sub.id] = dict(tz=sub.tz, channel=sub.channel_id)
    return subs_data


def get_quests_schedule(session):
    quests = (
        session
        .query(sql.Questionnaire)
        .filter(sql.Questionnaire.active)
        .all()
    )
    subs = __get_subs(session)
    quest_schedules = dict()
    for q in quests:
        if len(q.schedule) == 0:
            continue
        # BEGIN: creating quest.id->tz->[(subscr.id, subscriber.channel_id)]
        quest_tz = dict()
        for subscr in q.subscriptions:
            if not subscr.active:
                continue
            sub = subs.get(subscr.subscriber_id)
            quest_tz_subscr = __get_or_create(quest_tz, sub['tz'], [])
            quest_tz_subscr.append((subscr.id, sub['channel'],))
        # END: creating quest.id->tz->[(subscr.id, subscriber.channel_id)]
        # BEGIN: creating quest.id->[{days, time}]
        schedules = []
        for sch in q.schedule:
            days = [False]*7
            time = sch.time.strftime(TIME_FORMAT)
            for i in range(sch.start-1, sch.end):
                days[i] = True
            schedules.append(dict(days=days, time=time))
        # END: creating quest.id->[{days, time}]
        expiration = None
        if q.expiration is not None:
            expiration = q.expiration.strftime(TIME_FORMAT)
        quest_schedules[q.id] = dict(
            title=q.title,
            expiration=expiration,
            subscriptions=quest_tz,
            schedules=schedules
        )
    return quest_schedules


def update_timezones(timezones, id, quest):
    quest_tz = set([tz for tz in quest['subscriptions']])
    schedules = quest['schedules']
    for sch in schedules:
        days = sch['days']
        time = sch['time']
        for tz in quest_tz:
            tzdays = __get_or_create(
                timezones,
                tz,
                [dict() for i in range(0, 7)]
            )
            for i in range(len(days)):
                if days[i]:
                    tzday = tzdays[i]
                    tztime = __get_or_create(tzday, time, [])
                    tztime.append(id)


def get_execution_schedule(quest_schedules):
    timezones = dict()
    for id in quest_schedules:
        update_timezones(timezones, id, quest_schedules[id])
    return timezones


def get_plan(session):
    quests = get_quests_schedule(session)
    execution = get_execution_schedule(quests)
    return dict(quest=quests, execution=execution)


def load():
    with open(FILENAME, 'r') as f:
        return json.loads(f.read())


def update(session):
    with open(FILENAME, 'w') as f:
        f.write(json.dumps(get_plan(session), indent=4))
