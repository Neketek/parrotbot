from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from functools import wraps
from modules.config.env import config as envconf


engine = create_engine('sqlite:///dbvolume/db.sqlite', echo=envconf.DB_DEBUG)
Base = declarative_base()
Session = sessionmaker(bind=engine)


def session(key="session"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                session = Session()
                session.execute('PRAGMA foreign_keys=ON')
                kwargs = dict(kwargs)
                kwargs[key] = session
                return func(*args, **kwargs)
            finally:
                session.close()
        return wrapper
    return decorator
