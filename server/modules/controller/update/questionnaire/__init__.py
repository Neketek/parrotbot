from modules.controller.core import actions as a, Conditions as c
from modules.controller import permission
from modules.config.naming import short
from modules.model import sql
from modules.controller.create.questionnaire.download_template import\
    download_template
from .schema import TemplateSchema
from .json_to_str import json_to_str
from .save import save
from modules.controller.core import utils
from .help_text import TEXT as HTEXT

__CMD = (short.method.update, short.name.questionnaire,)

CMD = utils.cmd_str(*__CMD)

ERROR = """
Update stoped. Error:
{}
"""


@a.register(c.command(*__CMD, cmd_str=CMD, cmd_help=HTEXT))
@sql.session()
@permission.admin()
def questionnaire(c, session=None):
    try:
        if c.i is None:
            return (
                c.reply_and_wait("Waiting for update file...")
                .interactive("file")
            )
        elif c.i.next == "file":
            return download_template(c, TemplateSchema, json_to_str)
        elif isinstance(c.i.next, dict):
            if c.command == 'yes':
                c.reply("Updating questionnaire...")
            elif c.command == 'no':
                return c.reply_and_wait('Update canceled.')
            else:
                return c.reply_and_wait('yes|no?').interactive(c.i.next)
            return save(c, session)
    except ValueError as e:
        return c.reply_and_wait(ERROR.format(e))
