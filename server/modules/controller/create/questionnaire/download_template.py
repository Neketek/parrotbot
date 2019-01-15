from marshmallow import ValidationError
import json
from requests import RequestException


SUCCESSFULL_REPLY_TEMPLATE = """
File was loaded and parsed succesfully.
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
File schema is not valid.
Reason:
{0}
"""


def download_template(c, SchemaCls, json_to_str):
    try:
        if c.file is None:
            raise ValueError(NO_FILE_ERROR)
        c.reply('Loading the template file...')
        data = json.loads(c.load_file_request().content)
        SchemaCls().load(data)
        return c.reply_and_wait(
            SUCCESSFULL_REPLY_TEMPLATE.format(json_to_str(data))
        ).interactive(data)
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
