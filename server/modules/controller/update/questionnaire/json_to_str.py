from modules.controller.create.questionnaire.json_to_str import\
    list_to_str, schedule_list_to_str

TEMPLATE = """
Name:{}
"""


def json_to_str(data):
    result = TEMPLATE.format(data['name'])
    try:
        result += "\nTitle:{}".format(data['title'])
    except KeyError:
        pass
    try:
        result += "\nExpiration: {}".format(data['expiration'])
    except KeyError:
        pass
    try:
        result += "\nRetention: {}".format(data['retention'])
    except KeyError:
        pass
    try:
        result += "\nSubscribers:\n{}".format(
            list_to_str(data['subscribers'])
        )
    except KeyError:
        pass
    try:
        result += "\nSchedule:\n{}".format(
            schedule_list_to_str(data['schedule'])
        )
    except KeyError:
        pass
    return result
