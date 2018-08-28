"""
TMP : for testing
"""
from object import StateTransferObject, NEW, DONE
from scheduler import ThreadScheduler
from exceptions import NoObjectInterrupt
from db_session import Session
import config

import logging
from sqlalchemy import create_engine

_log = logging.getLogger(__name__)


class DefaultEntry(object):
    def __init__(self):
        self._engine = None
        self._session = None
        self._scheduler = ThreadScheduler()
        self._objs = set()
        self._init_db()
        self._support_sto = set([StateTransferObject])

    def add_custom_state_transfer_obj(self, sto_cls):
        if not issubclass(sto_cls, StateTransferObject):
            raise TypeError('Only support add subclass of StateTransferObject')
        self._support_sto.add(sto_cls)
        sto_cls.metadata.create_all(self._engine)

    def _init_db(self):
        if config.DB_URL.startswith("sqlite"):
            # XXX: or reject use ThreadScheduler ?
            self._engine = create_engine(config.DB_URL,
                                         connect_args={'check_same_thread': False})
        else:
            self._engine = create_engine(config.DB_URL)
        Session.create_session(self._engine)
        self._session = Session.get_session()
        StateTransferObject.metadata.create_all(self._engine)

    def register_obj(self, obj):
        self._objs.add(obj)
        self._session.add(obj)

    def deregister_obj(self, obj):
        self._objs.remove(obj)
        self._session.delete(obj)

    def db_commit(self):
        self._session.commit()

    def db_check_update(self):
        for obj in self._session.dirty:
            yield obj, False
        for obj in self._session.new:
            yield obj, True

    def next(self, new_objs=None, ignore_obj=False):
        if new_objs:
            for obj in new_objs:
                self.register_obj(obj)
            self.db_commit()

        if not self._objs:
            raise NoObjectInterrupt('Need obj for next iterate')

        self._scheduler.new_task(self._objs)
        self._scheduler.wait_all_task()

        for obj, new_one in self.db_check_update():
            if new_one:
                if obj.__class__ not in self._support_sto:
                    if ignore_obj:
                        continue
                    else:
                        raise TypeError('Not support %s' % obj.__class__.__name__)
                _log.info('Find a new obj %s', obj)
                self.register_obj(obj)
            if obj.state == DONE:
                _log.info('%s have finished it lifecycle', obj)
                self.deregister_obj(obj)

        self.db_commit()


if __name__ == '__main__':
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
