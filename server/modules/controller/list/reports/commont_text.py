DAYS_RANGE_IS_NOT_INT = """
<days> should be int.
{}
"""

NO_DAYS_RANGE = """
Pls, provide days range.
{}
"""


NOT_SUBSCRIBER = """
You're not a subscriber. Can't get your timezone.
Pls, update subscribers.
"""


def no_names(msg_format, names):
    return msg_format.format(
        "\n".join(
            "\t{}. {}".format(i+1, n)
            for i, n in zip(range(len(names)), names)
        )
    )


def no_days_range(command):
    return NO_DAYS_RANGE.format(command)


def days_range_is_not_int(command):
    return DAYS_RANGE_IS_NOT_INT.format(command)
