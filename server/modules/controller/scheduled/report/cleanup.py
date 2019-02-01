from modules.model import sql
from sqlalchemy import func
from modules.logger import root as logger


def cleanup(session, utc_now):
    ids = (
        session
        .query(sql.Report.id)
        .join(sql.Subscription)
        .join(sql.Questionnaire)
        .filter(
            func.datetime(
                sql.Report.utc_expiration,
                func.printf(
                    "+%i day",
                    sql.Questionnaire.retention
                )
            ) < utc_now
        )
    )
    deleted_reports = (
        session
        .query(sql.Report)
        .filter(sql.Report.id.in_(ids.subquery()))
        .delete(synchronize_session=False)
    )
    archived_subs_with_no_reports = (
        session
        .query(sql.Subscriber.id)
        .join(sql.Subscription)
        .outerjoin(sql.Report)
        .filter(sql.Subscriber.archived)
        .group_by(sql.Subscriber.id)
        .having(func.sum(sql.Report.completed.isnot(None)))
    )
    deleted_archived_subs = (
        session
        .query(sql.Subscriber)
        .filter(
            sql.Subscriber.id.in_(
                archived_subs_with_no_reports.subquery()
            )
        )
        .delete(synchronize_session=False)
    )
    session.commit()
    if deleted_archived_subs + deleted_reports > 0:
        logger.info("Cleanup...")
        logger.info(
            'Reports cleanup. Deleted {} reports'.format(deleted_reports)
        )
        logger.info('{} archived users deleted'.format(
            deleted_archived_subs)
        )
