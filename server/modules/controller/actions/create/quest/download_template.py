from .schema import TemplateSchema
from marshmallow import ValidationError
import json
from requests import RequestException


DATA_STR_TEMPLATE = """
Title:{title}
Questions:
{questions}
Subscribers:
{subscribers}
Schedule:
{schedule}
"""

SUCCESSFULL_REPLY_TEMPLATE = """
Template file was loaded and parsed succesfully.
Is everything below correct?
{0}
yes|no?
"""

NO_FILE_ERROR = """
Can't find the template file.
Creation stopped.
"""

JSON_DECODE_ERROR = """
Can't decode json. File is invalid json.
Creation stopped.
"""

REQUEST_ERROR = """
Can't download template file from slack.
Creation stopped.
Error:
{0}
"""

INVALID_SCHEMA_ERROR = """
Template schema is not valid:
Creation stopped.
Errors:
{0}
"""


def data_to_str(data):
    def list_to_str(l, format=str):
        r = ''
        n = 1
        for i in l:
            r += '\t{0}) {1}\n'.format(n, format(i))
            n += 1
        return r
    return DATA_STR_TEMPLATE.format(
        title=data['title'],
        questions=list_to_str(data['questions']),
        subscribers=list_to_str(data['subscribers']),
        schedule=list_to_str(
            [
                (
                    '{}-{}'.format(s['start'], s['end']),
                    s['time'],
                )
                for s in data['schedule']
            ],
            format=lambda s: ' '.join(s)
        )
    )


def download_template(c):
    try:
        if c.file is None:
            raise ValueError(NO_FILE_ERROR)
        c.reply('Loading the template file...')
        data = json.loads(c.load_file_request().content)
        TemplateSchema().load(data)
        c.reply(SUCCESSFULL_REPLY_TEMPLATE.format(data_to_str(data)))
        return c.interactive(data)
    except json.JSONDecodeError:
        c.reply(JSON_DECODE_ERROR)
        return
    except RequestException as e:
        c.reply(REQUEST_ERROR.format(e))
    except ValidationError as e:
        c.reply(
            INVALID_SCHEMA_ERROR.format(
                json.dumps(e.messages, indent=4)
            )
        )
