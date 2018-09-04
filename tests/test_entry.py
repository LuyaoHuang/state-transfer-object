import pytest

from state_transfer_object.entry import DefaultEntry, ContEntry
from state_transfer_object.db_session import Session
from state_transfer_object.object import StateTransferObject, NEW, DONE
from state_transfer_object.exceptions import NoObjectInterrupt


def test_entry():
    sto_1 = StateTransferObject(state=NEW)
    test_entry = DefaultEntry()
    test_entry.next(new_objs=[sto_1])

    with pytest.raises(NoObjectInterrupt):
        test_entry.next()

    assert sto_1.state == DONE


class CustomObject(StateTransferObject):
    def iterate(self):
        if self.state == NEW:
            tmp = StateTransferObject(state=NEW)
            self.transfer_state(DONE)
        else:
            raise Exception('Unsupported state: %s' % self.state)


def test_cont_entry():
    sto_1 = CustomObject(state=NEW)
    test_entry = ContEntry()
    test_entry.add_custom_state_transfer_obj(CustomObject)
    test_entry.start([sto_1])
    test_entry.wait()
    assert sto_1.state == DONE
