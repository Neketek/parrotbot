from modules.model import sql
from sqlalchemy.orm import exc as orme
from datetime import datetime, timedelta
from pytz import timezone

REPORT_MESSAGE = """
Pls, provide report on "{title}" questionnaire.
You have {time} from this moment to answer the questions.
Type "report" when you're ready.
"""


NO_QUEST = """
Can't find questionarie "{}"
"""


def create_report_request_msg(quest, now, tz):
    if quest.expiration is None:
        next = tz.localize(
            datetime.combine(
                (now + timedelta(days=1)).date(),
                datetime.min.time()
            )
        )
        time = next - now
        h = time.seconds // 3600
        m = (time.seconds % 3600)//60

    else:
        h = quest.expiration.hour
        m = quest.expiration.minute
    return REPORT_MESSAGE.format(
        title=quest.title,
        time="{}h {}m".format(h, m)
    )


@sql.session()
def request_report(c, quest=None, title=None, session=None):
    if quest is None:
        if title is not None:
            try:
                quest = session\
                    .query(sql.Questionnaire)\
                    .filter(sql.Questionnaire.title == title)\
                    .one()
            except orme.NoResultFound:
                raise ValueError(NO_QUEST.format(title))
    now = timezone('UTC').localize(datetime.utcnow())
    msg = dict()
    for s in quest.subscriptions:
        tz = timezone(s.subscriber.tz)
        created = now.astimezone(tz)
        session.add(
            sql.Report(
                subscription=s,
                created=created
            )
        )
        msg[s.subscriber.tz] = create_report_request_msg(quest, created, tz)
    session.commit()
    for s in quest.subscriptions:
        c.send(s.subscriber.channel_id, msg[s.subscriber.tz])
