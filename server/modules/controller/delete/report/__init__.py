from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
from modules.config.naming import short
from modules.controller.set.common.checks import compare_found_expected
from modules.controller import permission
from modules.controller.core import utils
from .help_text import TEXT as HTEXT

__CMD = (short.method.delete, short.name.report,)
__PARAMS = [
    "{}_id,...".format(short.name.report)
]
CMD = utils.cmd_str(*__CMD, params=__PARAMS)

NO_IDS = """
Pls, provide id(s).
{}
""".format(CMD)


@a.register(c.command(*__CMD, cmd_str=CMD, cmd_help=HTEXT))
@sql.session()
@permission.admin()
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
