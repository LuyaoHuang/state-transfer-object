"""
State Transfer Object
"""
from state import State, StateManager
from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StateTransferObject(Base):
    """ TODO
    """
    __tablename__ = 'state_trans_objs'

    id = Column(Integer, primary_key=True)
    state = Column(String)

    def transfer_state(self, new_state):
        self.state = new_state
