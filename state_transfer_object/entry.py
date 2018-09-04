"""
TMP : for testing
"""
from .object import StateTransferObject, NEW, DONE
from .scheduler import ThreadScheduler
from .exceptions import NoObjectInterrupt, NotSupportedError
from .db_session import Session
from . import config

import logging
from sqlalchemy import create_engine, event

_log = logging.getLogger(__name__)


class DefaultEntry(object):
    """ This is a noncontinuous call entry
        it require call next() method to trigger next iteration
    """
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
        Session.create_session(self._engine, autocommit=False)
        self._session = Session.get_session()
        StateTransferObject.metadata.create_all(self._engine)

    def register_obj(self, obj):
        self._objs.add(obj)
        self._session.add(obj)

    def deregister_obj(self, obj, db_rm=False):
        self._objs.remove(obj)
        if db_rm:
            self._session.delete(obj)

    def db_commit(self):
        self._session.commit()

    def db_check_update(self):
        for obj in self._session.dirty:
            yield obj, False
        for obj in self._session.new:
            yield obj, True

    def _check_state_transfer(self, ignore_obj):
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

    def next(self, new_objs=None, ignore_obj=False):
        if new_objs:
            for obj in new_objs:
                self.register_obj(obj)
        self.db_commit()

        if not self._objs:
            raise NoObjectInterrupt('Need obj for next iterate')

        self._scheduler.new_task(self._objs)
        self._scheduler.wait_all_task()
        self._check_state_transfer(ignore_obj)
        self.db_commit()


class ContEntry(DefaultEntry):
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

    def start(self, objs):
        if not objs:
            raise NoObjectInterrupt('Need obj for next iterate')

        for obj in objs:
            self.register_obj(obj)

        self._register_event()

        self._scheduler.new_task(objs)

    def wait(self):
        self._scheduler.wait_all_task()
        if self._objs:
            _log.warning('Some objs not finished: %s', self._objs)

        self._deregister_event()

    def next(self):
        raise NotSupportedError('Cannot use next method in a continuous entry')

    def _register_event(self):
        for sto_cls in self._support_sto:
            event.listen(sto_cls, 'init', self._obj_init_callback)
            event.listen(sto_cls.state, 'set', self._obj_state_callback)

    def _deregister_event(self):
        for sto_cls in self._support_sto:
            event.remove(sto_cls, 'init', self._obj_init_callback)
            event.remove(sto_cls.state, 'set', self._obj_state_callback)

    def _obj_init_callback(self, target, args, kwargs):
        _log.info('new obj init %s %s %s', target, args, kwargs)

    def _obj_state_callback(self, target, value, oldvalue, initiator):
        _log.info('%s state change %s -> %s', target, oldvalue, value)
        if value == DONE:
            _log.info('%s have finished it lifecycle', target)
            self.deregister_obj(target)
        elif value == NEW:
            self._objs.add(target)
            self._scheduler.new_task([target])
        else:
            # TODO
            pass
