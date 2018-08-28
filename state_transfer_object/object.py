"""
State Transfer Object
"""
from .state import State, StateManager
from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Supported state
# TODO: use a class and move to a new file
NEW = "New"
DONE = "Done"


class StateTransferObject(Base):
    """ TODO
    """
    __tablename__ = 'state_trans_objs'

    id = Column(Integer, primary_key=True)
    state = Column(String)

    # __mapper_args__ = {
    #     'polymorphic_on': type,
    #     'polymorphic_identity': 'state_trans_objs'
    # }

    def transfer_state(self, new_state):
        self.state = new_state

    def iterate(self):
        """ This is a example, Override this method
        """
        if self.state == NEW:
            self.transfer_state(DONE)
        return
