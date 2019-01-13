from modules.model import sql
from sqlalchemy import func


def cleanup(session, utc_now):
    ids = (
        session
        .query(sql.Report.id)
        .join(sql.Subscription)
        .join(sql.Questionnaire)
        .filter(
            func.date(
                sql.Report.utc_expiration,
                func.printf(
                    "+{} day",
                    sql.Questionnaire.retention
                )
            ) < utc_now
        )
    )
    (
        session
        .query(sql.Report)
        .filter(sql.Report.id.in_(ids.subquery()))
        .delete(synchronize_session=False)
    )
    session.commit()
