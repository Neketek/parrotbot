from modules.model import sql
from sqlalchemy.orm import exc as orme
from datetime import timedelta
from modules.controller.core.time import get_tomorrow, get_utcnow
from pytz import timezone


REPORT_MESSAGE = """
Pls, provide report on "{title}" questionnaire.
You have {time} from this moment to answer the questions.
Type `report` when you're ready.
"""


NO_QUEST = """
Can't find questionarie "{}"
"""


def get_expiration(quest, now, utc_now, tz):
    t = quest.expiration
    if t is None:
        next = get_tomorrow(tz)
        dt = next - now
    else:
        dt = timedelta(hour=t.hour, minute=t.minute)
    return now + dt, utc_now + dt, dt


def create_report_request_msg(quest, dt):
    h = dt.seconds // 3600
    m = dt.seconds % 3600 // 60
    return REPORT_MESSAGE.format(
        title=quest.title,
        time="{}h {}m".format(h, m)
    )


@sql.session()
def request_report(c, quest=None, name=None, session=None):
    if quest is None:
        if name is not None:
            try:
                quest = session\
                    .query(sql.Questionnaire)\
                    .filter(sql.Questionnaire.name == name)\
                    .one()
            except orme.NoResultFound:
                raise ValueError(NO_QUEST.format(name))
    now = get_utcnow()
    msg = dict()
    for s in quest.subscriptions:
        if not s.subscriber.active or s.subscriber.archived:
            continue
        tz = timezone(s.subscriber.tz)
        created = now.astimezone(tz)
        expiration, utc_expiration, dt = get_expiration(
            quest,
            created,
            now,
            tz
        )
        session.add(
            sql.Report(
                subscription=s,
                created=created,
                expiration=expiration,
                utc_expiration=utc_expiration
            )
        )
        msg[s.subscriber.tz] = create_report_request_msg(quest, dt)
    session.commit()
    for s in quest.subscriptions:
        c.send(s.subscriber.channel_id, msg[s.subscriber.tz])
