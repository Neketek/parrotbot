from modules.model.sql import Questionnaire


DATA_STR_TEMPLATE = """
Name: {name}
Title: {title}
Retention: {retention} day(s)
Expiration: {expiration}
Questions:
{questions}
Subscribers:
{subscribers}
Schedule:
{schedule}
"""


def __list_to_str(l, format=str):
    r = ''
    n = 1
    for i in l:
        r += '\t{0}) {1}\n'.format(n, format(i))
        n += 1
    return r


def json_to_str(data):
    return DATA_STR_TEMPLATE.format(
        name=data['name'],
        title=data['title'],
        expiration=data.get('expiration', Questionnaire.NULL_EXPIRATION_STR),
        retention=data.get('retention', Questionnaire.DEFAULT_RETENTION),
        questions=__list_to_str(data['questions']),
        subscribers=__list_to_str(data['subscribers']),
        schedule=__list_to_str(
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
