from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from modules.config.naming import short
from modules.controller.set.common.checks import compare_found_expected


NO_QUEST_NAMES = """
Pls, provide questionnaire name(s).
"""


@a.register(c.command(short.method.delete, short.name.questionnaire))
@sql.session()
def questionnaire(c, session=None):
    names = c.cs_command_args[2:]
    if len(names) == 0:
        return c.reply_and_wait(NO_QUEST_NAMES)
    quests_query = (
        session
        .query(sql.Questionnaire)
        .filter(sql.Questionnaire.name.in_(names))
    )
    quests = quests_query.all()
    try:
        compare_found_expected(
            quests,
            names,
            lambda q: q.name,
            "Questionnaire(s):"
        )
    except ValueError as e:
        return c.reply_and_wait(e)
    quests_query.delete(synchronize_session=False)
    session.commit()
    return c.reply_and_wait(
        'Done. {} questionnaire(s) deleted.'
        .format(len(names))
    )
