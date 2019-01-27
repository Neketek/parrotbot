from .constant import REPORT_REQUEST_MSG_FORMAT, TIME_FORMAT
from datetime import datetime, timedelta
from modules.controller.core.time import \
    get_relative_shifted_date_start
from modules.controller.core import exc as cexc
from pytz import timezone
from modules.model import sql
import json
from modules.logger import root as logger


def __get_or_create(t, k, d):
    try:
        return t[k]
    except KeyError:
        t[k] = d
        return d


def create_msg(title, td):
    hours = td.seconds // 3600
    minutes = (td.seconds - 3600 * hours) // 60
    return REPORT_REQUEST_MSG_FORMAT.format(
        title=title,
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
        return source.strftime("%d-%m-%Y %H:%M")
    else:
        return source


def __dump_to_file(fname, source):
    with open(fname, "w") as f:
        f.write(
            json.dumps(
                __dict_to_json_dict(source),
                indent=4
            )
        )


def send(c, session, plan, utcnow):
    execution_plan = plan['execution']
    quest_plan = plan['quest']
    if not quest_plan:
        logger.debug("Scheduled reports empty quest plan!")
        return
    report_requests = dict()
    # building report requests
    # quest_id->creation_time->subscriptions->[(subscr.id, channel)]
    for tz, tzdays in execution_plan.items():
        tzdatetime = utcnow.astimezone(timezone(tz))
        tztime = tzdatetime.time().strftime("%H:%M")
        tztime = tzdays[tzdatetime.weekday()].get(tztime)
        logger.debug("CHECKING TZ")
        logger.debug(
            "TZ:{} DT:{} WD:{}".format(tz, tzdatetime, tzdatetime.weekday())
        )
        logger.debug("TZ TIME FOUND?:{}".format(tztime is not None))
        if tztime is None:
            continue
        for qid in tztime:
            subscriptions = quest_plan[str(qid)]['subscriptions'][tz]
            quest_report_requests = __get_or_create(
                report_requests,
                qid,
                dict()
            )
            quest_subscriptions = __get_or_create(
                quest_report_requests,
                tzdatetime,
                list()
            )
            quest_subscriptions += subscriptions
    # empty dict evaluates as false, here is small optimization
    if not report_requests:
        logger.debug(
            "Scheduled report request targets not found! UTC:{}".format(utcnow)
        )
        return
    logger.debug(
        'Scheduled report request targets found! UTC:{}'.format(utcnow)
    )
    # __dump_to_file("report_requests.json", report_requests)
    msgs = []
    reports = []
    for qid, request in report_requests.items():
        quest = quest_plan[str(qid)]
        title = quest['title']
        expiration = quest['expiration']
        for created, subscriptions in request.items():
            if expiration is None:
                expiration = get_relative_shifted_date_start(created, 1)
                td = expiration - created
            else:
                etime = datetime.strptime(expiration, TIME_FORMAT).time()
                td = timedelta(hours=etime.hour, minutes=etime.minute)
                expiration = created + td
            utc_expiration = utcnow + td
            msg = create_msg(title, td)
            channels = []
            for id, channel in subscriptions:
                reports.append(
                    sql.Report(
                        subscription_id=id,
                        created=created,
                        expiration=expiration,
                        utc_expiration=utc_expiration
                    )
                )
                channels.append(channel)
            msgs.append((msg, channels,))
    # __dump_to_file("msgs.json", msgs)
    logger.debug('Saving report request db records:{}'.format(len(reports)))
    session.bulk_save_objects(reports)
    session.commit()
    logger.debug('Sending report request reminders...')
    for msg, channels in msgs:
        for ch in channels:
            try:
                c.send(ch, msg)
            except cexc.SlackAPICallException as e:
                logger.error(str(e))
