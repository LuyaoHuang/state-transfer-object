"""
Example 2
"""
import logging
import time

import os
import sys

# TODO: how to remove this ?
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.isdir(os.path.join(BASEDIR, 'state_transfer_object')):
    os.environ['PATH'] += ":" + os.path.join(BASEDIR, 'tests')
    sys.path.insert(0, BASEDIR)

from state_transfer_object.entry import ContEntry
from state_transfer_object.db_session import Session
from state_transfer_object.object import StateTransferObject, NEW, DONE

_log = logging.getLogger(__name__)


class CustomObject(StateTransferObject):
    def iterate(self):
        if self.state == NEW:
            _log.info('Create a new obj')
            tmp = StateTransferObject(state=NEW)
            Session.add_obj(tmp)
            self.transfer_state(DONE)
        else:
            raise Exception('Unsupported state: %s' % self.state)


logging.basicConfig(level=logging.INFO)

sto_1 = CustomObject(state=NEW)
test_entry = ContEntry()
test_entry.add_custom_state_transfer_obj(CustomObject)
test_entry.start([sto_1])
time.sleep(1)
test_entry.wait()
_log.info('PASS!!!!')
