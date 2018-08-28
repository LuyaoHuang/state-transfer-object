"""
Shared database session
"""

from sqlalchemy.orm import sessionmaker
from exceptions import SessionNotInitError


class Session(object):
    _session = None

    @classmethod
    def create_session(cls, engine):
        cls._session = sessionmaker(bind=engine)()

    @classmethod
    def get_session(cls):
        if not cls._session:
            raise SessionNotInitError
        return cls._session

    @classmethod
    def close_session(cls):
        if not cls._session:
            raise SessionNotInitError
        cls._session.close()

    @classmethod
    def add_obj(cls, obj):
        if not cls._session:
            raise SessionNotInitError
        cls._session.add(obj)

    @classmethod
    def del_obj(cls, obj):
        if not cls._session:
            raise SessionNotInitError
        cls._session.delete(obj)
