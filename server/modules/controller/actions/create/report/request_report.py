from modules.model import sql
from sqlalchemy.orm import exc as orme
from datetime import datetime

REPORT_MESSAGE = """
Please provide report on "{title}" questionnaire.
You have {time} from this moment to answer the question.
Type "report" to tell me that you're ready to provide questions.
"""


def create_report_request_msg(quest):
    return REPORT_MESSAGE.format(
        title=quest.title,
        time="1h00m"
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
                raise ValueError(
                    "Can't find questionnaire \"{}\"".format(title)
                )
    for s in quest.subscriptions:
        session.add(
            sql.Report(
                subscription=s,
                created=datetime.now()
            )
        )
    session.commit()
    msg = create_report_request_msg(quest)
    for s in quest.subscriptions:
        c.send(s.subscriber.channel_id, msg)
