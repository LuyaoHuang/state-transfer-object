"""
Example 1
"""
import logging

import os
import sys

# TODO: how to remove this ?
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.isdir(os.path.join(BASEDIR, 'state_transfer_object')):
    os.environ['PATH'] += ":" + os.path.join(BASEDIR, 'tests')
    sys.path.insert(0, BASEDIR)

from state_transfer_object.entry import DefaultEntry
from state_transfer_object.object import StateTransferObject, NEW, DONE
from state_transfer_object.exceptions import NoObjectInterrupt

_log = logging.getLogger(__name__)


logging.basicConfig(level=logging.INFO)
sto_1 = StateTransferObject(state=NEW)
test_entry = DefaultEntry()
test_entry.next(new_objs=[sto_1])
try:
    test_entry.next()
except NoObjectInterrupt:
    _log.info('Cool !')
else:
    _log.error('WTF ?')
