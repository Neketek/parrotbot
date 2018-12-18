from modules.model import sql
from modules.controller.core import actions as a, Conditions as c
from sqlalchemy import func, and_, or_
from datetime import datetime
from sqlalchemy.orm import exc as orme


@a.register(c.command('update', 'report'))
@sql.session()
def update_report(c, session=None):
    pass
