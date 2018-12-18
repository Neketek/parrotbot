from datetime import datetime, timedelta
from pytz import timezone


def get_utcnow():
    return timezone('UTC').localize(datetime.utcnow())


def get_now(tz):
    return get_utcnow().astimezone(tz)


def get_today(tz):
    return get_now(tz).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )


def get_tomorrow(tz):
    return get_today(tz)+timedelta(days=1)
