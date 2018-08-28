import pytest

from state_transfer_object.entry import DefaultEntry
from state_transfer_object.object import StateTransferObject, NEW, DONE
from state_transfer_object.exceptions import NoObjectInterrupt


def test_entry():
    sto_1 = StateTransferObject(state=NEW)
    test_entry = DefaultEntry()
    test_entry.next(new_objs=[sto_1])

    with pytest.raises(NoObjectInterrupt):
        test_entry.next()

    assert sto_1.state == DONE
