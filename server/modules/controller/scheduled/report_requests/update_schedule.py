from modules.model import sql
from sqlalchemy import not_
import json


def get_sub_tz(session):
    sub_tz = dict()
    subs = (
        session
        .query(sql.Subscriber)
        .filter(sql.Subscriber.active)
        .filter(not_(sql.Subscriber.archived))
        .all()
    )
    for sub in subs:
        sub_tz[sub.id] = sub.tz
    return sub_tz


def get_quests_schedule(session):
    quests = (
        session
        .query(sql.Questionnaire)
        .filter(sql.Questionnaire.active)
        .all()
    )
    sub_tz = get_sub_tz(session)
    quest_schedules = dict()
    for q in quests:
        if len(q.schedule) == 0:
            continue
        quest_tz = dict()
        for subscr in q.subscriptions:
            tz = sub_tz.get(subscr.subscriber_id)
            if tz is not None:
                try:
                    quest_tz_sub = quest_tz[tz]
                except KeyError:
                    quest_tz_sub = []
                    quest_tz[tz] = quest_tz_sub
                quest_tz_sub.append(subscr.id)
        schedules = []
        for sch in q.schedule:
            days = [False]*7
            time = str(sch.time)
            for i in range(sch.start-1, sch.end):
                days[i] = True
            schedules.append(dict(days=days, time=time))
        quest_schedules[q.id] = dict(
            subscriptions=quest_tz,
            schedules=schedules
        )
    return quest_schedules


def update_timezones(timezones, id, quest):
    quest_timezones = set([tz for tz in quest['subscriptions']])
    schedules = quest['schedules']
    for sch in schedules:
        days = sch['days']
        time = sch['time']
        for tz in quest_timezones:
            try:
                tzdays = timezones[tz]
            except KeyError:
                tzdays = [dict() for i in range(0, 7)]
                timezones[tz] = tzdays
            for i in range(len(days)):
                if days[i]:
                    daytime = tzdays[i]
                    try:
                        questtime = daytime[time]
                    except KeyError:
                        questtime = []
                        daytime[time] = questtime
                    questtime.append(id)


def get_execution_schedule(quest_schedules):
    timezones = dict()
    for id in quest_schedules:
        update_timezones(timezones, id, quest_schedules[id])
    return timezones


def get_schedule(session):
    quests = get_quests_schedule(session)
    execution = get_execution_schedule(quests)
    return dict(quest=quests, execution=execution)


def update_schedule(session):
    with open("schedule.json", "w") as f:
        f.write(json.dumps(get_schedule(session), indent=4))
