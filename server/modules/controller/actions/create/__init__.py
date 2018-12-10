from modules.controller.core import actions as a, Conditions as c
from modules.model import sql
import json


@a.register(c.command('create', 'quest'))
def create(c):
    if c.next is None or c.next == 'retry':
        c.reply(
            "Waiting for questionnaire file"
        )
        return c.interactive('file')
    elif c.next == 'file':
        if len(c.files) < 1:
            c.reply(
                "Unable to find file in the message.\nCreation stopped"
            )
        elif len(c.files) > 1:
            c.reply(
                'Too many files, pls provide single file.\nCreation stopped.'
            )
        else:
            c.reply("Loading file...")
            try:
                data = json.loads(c.load_file(c.files[0]))
                q = sql.Questionnaire.from_json(data)
                c.reply(
                    'File was loaded successfuly!\n'
                    + 'Is all below correct?\n\n'
                    + q.__repr__() + '\n\n'
                    + 'yes|no?'
                )
                return c.interactive(data)
            except ValueError:
                c.reply(
                    'questionnaire file is incorrect.\n Creation stopped.'
                )
            except json.JSONDecodeError:
                c.reply(
                    'Unable to decode json.'
                    + ' Is {0} a valid json?\n'
                    + 'Creation stopped.'
                    .format(c.files[0]['name'])
                )
            except Exception as e:
                c.reply(
                    'Unable to load file.\n'
                    + 'Creation stopped.\n'
                    + 'Error:' + str(e)
                )
    elif isinstance(c.next, dict):
        if c.command == 'yes':
            c.reply('OK!')
        elif c.command == 'no':
            c.reply('Nooo!')
        else:
            c.reply('Type "yes" or "no". Waiting...')
            return c.interactive(c.next)
