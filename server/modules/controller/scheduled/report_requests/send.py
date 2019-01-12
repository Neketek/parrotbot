from datetime import datetime, timedelta
from modules.controller.core.time import \
    get_utcnow, get_relative_shifted_date_start
from pytz import timezone
from modules.model import sql
import json


REPORT_REQUEST_MSG_FORMAT = """
Pls, provide report on {title} questionnaire.
You have {hours}h {minutes}m from this moment to answer the questions.
"""


def get_or_create(t, k, d):
    try:
        return t[k]
    except KeyError:
        t[k] = d
        return d


def create_msg(quest, created, expiration):
    if quest.expiration is None:
        td = expiration - created
        hours = td.seconds // 3600
        minutes = (td.seconds - 3600 * hours) // 60
    else:
        hours = quest.expiration.hour
        minutes = quest.expiration.minute
    return REPORT_REQUEST_MSG_FORMAT.format(
        title=quest.title,
        hours=hours,
        minutes=minutes
    )


def __dict_to_json_dict(source):
    if isinstance(source, dict):
        result = dict()
        for key, item in source.items():
            result[__dict_to_json_dict(key)] = __dict_to_json_dict(item)
        return result
    elif isinstance(source, list):
        return [__dict_to_json_dict(i) for i in source]
    elif isinstance(source, datetime):
        return source.strftime("%d-%m %H:%M")
    else:
        return source


def send(c, session, plan):
    curdatetime = get_utcnow()
    # curdatetime = get_utcnow().replace(day=8, hour=18, minute=0)
    execution_plan = plan['execution']
    quest_plan = plan['quest']
    report_requests = dict()
    # building report requests
    # quest_id->creation_time->subscriptions
    for tz, tzdays in execution_plan.items():
        tzdatetime = curdatetime.astimezone(timezone(tz))
        tztime = tzdatetime.time().strftime("%H:%M")
        tztime = tzdays[tzdatetime.weekday()].get(tztime)
        if tztime:
            for qid in tztime:
                subscriptions = quest_plan[str(qid)]['subscriptions'][tz]
                quest_report_requests = get_or_create(
                    report_requests,
                    qid,
                    dict()
                )
                quest_subscriptions = get_or_create(
                    quest_report_requests,
                    tzdatetime,
                    list()
                )
                quest_subscriptions += subscriptions
    # empty dict evaluates as false, here is small optimization
    if not report_requests:
        return
    with open("report_requests.json", "w") as f:
        f.write(
            json.dumps(
                __dict_to_json_dict(report_requests),
                indent=4
            )
        )
    # just to be sure that there are no dublicates
    # they should no appear in the lists but...
    quest_ids = []
    for qid, times in report_requests.items():
        quest_ids.append(qid)
        for t in times:
            times[t] = set(times[t])
    msgs = []
    quests = (
        session
        .query(sql.Questionnaire)
        .filter(sql.Questionnaire.id.in_(quest_ids))
        .all()
    )
    for quest in quests:
        times = report_requests[quest.id]
        for created, subscriptions in times.items():
            if quest.expiration is None:
                expiration = get_relative_shifted_date_start(created)
            else:
                expiration = (
                    created
                    + timedelta(
                        hours=expiration.hours,
                        minutes=expiration.minutes
                    )
                )
            for subscr_id in subscriptions:
                session.add(
                    sql.Report(
                        created=created,
                        expiration=expiration,
                        subscription_id=subscr_id
                    )
                )
            subscribers = (
                session
                .query(sql.Subscriber)
                .join(sql.Subscription)
                .filter(sql.Subscription.id.in_(subscriptions))
                .all()
            )
            channels = [s.channel_id for s in subscribers]
            msg = create_msg(quest, created, expiration)
            msgs.append((msg, channels,))
    with open("msgs.json", "w") as f:
        f.write(
            json.dumps(
                __dict_to_json_dict(msgs),
                indent=4
            )
        )
    # for msg, channels in msgs:
    #     for ch in channels:
    #         c.send(ch, msg)
