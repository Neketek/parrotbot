from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from modules.config.naming import short
from modules.controller.set.common.checks import compare_found_expected


NO_IDS = """
Pls, provide report id(s).
"""


@a.register(c.command(short.method.delete, short.name.report))
@sql.session()
def report(c, session=None):
    ids = c.command_args[2:]
    if len(ids) == 0:
        return c.reply_and_wait(NO_IDS)
    reports_query = (
        session
        .query(sql.Report)
        .filter(sql.Report.id.in_(ids))
    )
    reports = reports_query.all()
    try:
        compare_found_expected(
            reports,
            ids,
            lambda r: r.id,
            "Report(s):"
        )
    except ValueError as e:
        return c.reply_and_wait(e)
    reports_query.delete(synchronize_session=False)
    session.commit()
    return c.reply_and_wait(
        "{} report(s) deleted."
        .format(len(ids))
    )
