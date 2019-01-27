from modules.controller.core import time as t, Context
from modules.model import sql
from .report import plan, send, cleanup
from threading import Thread
import time
import os
from modules.logger import root as logger


class Manager(object):
    def __init__(self, client):
        self.client = client
        self.last_minute_call = None
        self.last_hour_call = None
        self.report_plan_mtime = None
        self.report_plan = None

    def is_next_minute(self, now):
        if self.last_minute_call is None:
            return True
        return self.last_minute_call.minute != now.minute

    def is_next_hour(self, now):
        if self.last_hour_call is None:
            return True
        return self.last_hour_call.hour != now.hour

    def send_reports(self, now):
        try:
            current_report_plan_mtime = os.path.getmtime(plan.FILENAME)
        except FileNotFoundError:
            @sql.session()
            def update_plan(session=None):
                plan.update(session)
            update_plan()
            current_report_plan_mtime = os.path.getmtime(plan.FILENAME)

        if self.report_plan_mtime != current_report_plan_mtime:
            self.report_plan = plan.load()
            self.report_plan_mtime = current_report_plan_mtime

        @sql.session()
        def worker(session=None):
            send.send(
                Context(self.client),
                session,
                self.report_plan,
                now
            )
        thread = Thread(
            target=worker,
            name="scheduled.reports.send UTC:{}".format(now)
        )
        thread.start()

    def cleanup_reports(self, now):
        @sql.session()
        def worker(session=None):
            cleanup.cleanup(session, now)
        thread = Thread(
            target=worker,
            name="scheduled.reports.cleanup UTC:{}".format(now)
        )
        thread.start()

    def tick(self):
        now = t.get_utcnow()
        if self.is_next_minute(now):
            logger.debug("Scheduled manager minute tick:{}".format(now))
            self.last_minute_call = now
            self.send_reports(now)
        elif self.is_next_hour(now):
            logger.debug("Scheduled manager hour tick:{}".format(now))
            self.last_hour_call = now
            self.cleanup_reports(now)

    def start(self, main_thread):
        def worker():
            while main_thread.is_alive():
                self.tick()
                time.sleep(1)
        thread = Thread(target=worker, name="scheduled.Manger")
        thread.start()
        return thread
