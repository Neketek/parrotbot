from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from sqlalchemy.orm import exc as orme


@a.register(c.user_msg_edit())
@sql.session()
def answer(c, session=None):
    pmsg = c.message.get('previous_message')
    cmsg = c.message.get('message')
    try:
        answer = (
            session
            .query(sql.Answer)
            .filter(sql.Answer.id == pmsg['client_msg_id'])
            .one()
        )
    except orme.NoResultFound:
        return
    if answer.report.subscription.subscriber.id != pmsg['user']:
        return
    answer.text = cmsg['text']
    session.add(answer)
    session.commit()
