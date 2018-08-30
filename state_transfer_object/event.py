"""
Use sqlalchemy event
"""
from .object import StateTransferObject
from sqlalchemy import event
import logging

_log = logging.getLogger(__name__)

# TODO: move to entry and use class method as call back function

@event.listens_for(StateTransferObject, 'init')
def watch_sto_init(target, args, kwargs):
    _log.error('init %s %s %s', target, args, kwargs)


@event.listens_for(StateTransferObject.state, 'modified')
def watch_state_change(target, initiator):
    _log.error('modify %s %s', target, initiator)


@event.listens_for(StateTransferObject.state, 'set')
def watch_state_set(target, value, oldvalue, initiator):
    _log.error('set %s %s %s %s', target, value, oldvalue, initiator)
