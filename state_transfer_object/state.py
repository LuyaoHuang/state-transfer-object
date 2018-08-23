"""
State of object
"""
from exceptions import InvalidStatusError

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class State(Base):
    __tablename__ = 'states'
    _valid_state = []

    id = Column(Integer, primary_key=True)
    name = Column(String)
    reason = Column(String)
    time = Column(DateTime)

    def _check_state(self, state):
        if not self._valid_state:
            return

        if state not in self._valid_state:
            raise InvalidStatusError(state)

    def transfer(self, state):
        self._check_state(state)
        self.name = state


class StateManager(object):
    def __init__(self, valid_states):
        self._state_objs = []
        self._valid_states = []

    def check_state(self, obj):
        if obj.state not in self._valid_state:
            raise InvalidStatusError(obj.state)

    def manage_obj(self, obj):
        self.check_state(obj)
        self._state_objs.append(obj)
