import json
from modules.model import sql
from sqlalchemy import func


GET_USERS_LIST_ERROR = """
Can't get slack.users.list
Reason:
{0}
"""

WRONG_SLACK_USER_DATA = """
slack.users.list result does not match expected schema.
"""

UNABLE_TO_OPEN_CHANNEL = """
Unable to open channel with user:{{{id}, {name}}}.
Reason:
{reason}
"""


def get_users_list(c):
    result = c.client.api_call('users.list')
    error = result.get('error')
    if error is not None:
        raise ValueError(
            GET_USERS_LIST_ERROR.format(json.dumps(error, indent=4))
        )
    try:
        users = result['members']
        return [
            dict(
                id=u['id'],
                name=u['name'],
                display_name=u['profile']['display_name'],
                admin=u['is_admin'] or u['is_owner'],
                tz=u['tz']
            )
            for u in users
            if not u['is_bot'] and u['id'] != 'USLACKBOT' and not u['deleted']
        ]
    except KeyError:
        raise ValueError(WRONG_SLACK_USER_DATA)


def get_users_with_channels_data(c):
    users = get_users_list(c)
    for u in users:
        result = c.client.api_call(
            'im.open',
            user=u['id']
        )
        error = result.get('error')
        if error is not None:
            raise ValueError(
                UNABLE_TO_OPEN_CHANNEL
                .format(
                    id=u['id'],
                    name=u['name'],
                    reason=json.dumps(error, indent=4)
                )
            )
        u['channel_id'] = result['channel']['id']
    return users


def get_subs_query(session, ids):
    return (
        session
        .query(sql.Subscriber)
        .filter(sql.Subscriber.id.in_(ids))
    )


def try_to_delete_subs(session, ids):
    if not ids:
        return
    delete_plan = (
        session
        .query(
            sql.Subscriber.id.label('id'),
            (func.count(sql.Report.id) == 0).label('delete')
        )
        .outerjoin(sql.Subscription)
        .outerjoin(sql.Report)
        .filter(sql.Subscriber.id.in_(ids))
        .group_by(sql.Subscriber.id)
        .all()
    )
    delete_ids = []
    archive_ids = []
    for id, delete in delete_plan:
        if delete:
            delete_ids.append(id)
        else:
            archive_ids.append(id)
    if delete_ids:
        get_subs_query(session, delete_ids).delete(
            synchronize_session=False
        )
    if archive_ids:
        get_subs_query(session, archive_ids).update(
            {
                sql.Subscriber.archived: True
            },
            synchronize_session=False
        )


def update_subscribers(c, session):
    users = get_users_with_channels_data(c)
    subs = session.query(sql.Subscriber).all()
    # updating existing subs
    updated_subs_ids = []
    delete_subs_ids = []
    for s in subs:
        for u in users:
            if u['id'] == s.id:
                s.name = u['name']
                s.display_name = u['display_name']
                s.admin = u['admin']
                s.channel_id = u['channel_id']
                s.tz = u['tz']
                updated_subs_ids.append(s.id)
                session.add(s)
                break
        else:
            delete_subs_ids.append(s.id)
    try_to_delete_subs(session, delete_subs_ids)
    session.bulk_save_objects(
        [
            sql.Subscriber(**u)
            for u in users
            if u['id'] not in updated_subs_ids
        ]
    )
