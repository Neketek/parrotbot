from .schema import TemplateSchema
from marshmallow import ValidationError
import json
from requests import RequestException
from .json_to_str import json_to_str


SUCCESSFULL_REPLY_TEMPLATE = """
Template file was loaded and parsed succesfully.
Is everything below correct?
{0}
yes|no?
"""

NO_FILE_ERROR = """
Can't find the template file.
"""

JSON_DECODE_ERROR = """
Can't decode json. File is invalid json.
"""

REQUEST_ERROR = """
Can't download template file from slack.
Reason:
{0}
"""

INVALID_SCHEMA_ERROR = """
Template schema is not valid.
Reason:
{0}
"""


def download_template(c):
    try:
        if c.file is None:
            raise ValueError(NO_FILE_ERROR)
        c.reply('Loading the template file...')
        data = json.loads(c.load_file_request().content)
        TemplateSchema().load(data)
        c.reply(SUCCESSFULL_REPLY_TEMPLATE.format(json_to_str(data)))
        return c.interactive(data)
    except json.JSONDecodeError:
        raise ValueError(JSON_DECODE_ERROR)
    except RequestException as e:
        raise ValueError(REQUEST_ERROR.format(e))
    except ValidationError as e:
        raise ValueError(
            INVALID_SCHEMA_ERROR.format(
                json.dumps(e.messages, indent=4)
            )
        )
