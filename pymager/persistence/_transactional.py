"""
    PyMager RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of PyMager.

    PyMager is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyMager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with PyMager.  If not, see <http://www.gnu.org/licenses/>.

"""
import threading
import logging
import traceback
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session, backref #, eagerload

_sessionmaker = None # should be initialized by bootstrap
_threadlocal = threading.local()

logger = logging.getLogger("transactional")

def init(sessionmaker):
    global _sessionmaker
    _sessionmaker = sessionmaker

def transactional(f):
    def do(*args, **kwargs):
        def callback(session):
            return f(*args, **kwargs)
        return SessionTemplate(_sessionmaker).do_with_session(callback)
    return do

class SessionTemplate(object):
    """ Simple helper class akin to Spring-JDBC/Hibernate/ORM Template.
    It doesnt't commit nor releases resources if other do_with_session() calls are pending
    
    See http://www.sqlalchemy.org/trac/ticket/1084#comment:3 for suggestions on how to improve this
    without using a custom threadlocal variable
     """
    def __init__(self, sessionmaker):
        assert sessionmaker is not None
        self._sessionmaker = sessionmaker
        
    def do_with_session(self, session_callback):        
        try:
            session = begin_scope(self._sessionmaker)
            result = session_callback(session)
        except Exception as e1:
            try:
                _mark_as_rollback(self._sessionmaker)
            except Exception as e2:
                pass
            raise
        finally:
            end_scope(self._sessionmaker)
        return result

class BoundSession(object):
    def __init__(self, session, count=0):
        assert count >= 0
        self.session = session
        self.count = count
        self.should_commit = True
    
    def increment(self):
        self.count=self.count+1
    
    def decrement(self):
        self.count=self.count -1
    
    def rollback(self):
        self.should_commit = False

def begin_scope(session_maker):
    bound_session = _threadlocal.current_session if _session_exists() else BoundSession(session_maker())
    bound_session.increment()
    _threadlocal.current_session = bound_session
    return bound_session.session

def end_scope(session_maker, force_rollback=False):
    if _current_count() == 1:
        try:
            if (not force_rollback) and _should_commit():
                _session().commit()
            else:
                _rollback(session_maker)
        finally:
            _cleanup(session_maker)
    else:
        _threadlocal.current_session.decrement()

def _rollback(session_maker):
    #if not _session_exists():
    #    return
    
    try:
        conn = _session().connection().invalidate()
    except sqlalchemy.exc.InvalidRequestError:
        # ignore the following exception that happens on windows... 
        # InvalidRequestError("The transaction is inactive 
        # due to a rollback in a subtransaction and should be closed")
        #
        pass
    except Exception:
        pass
    
    _session().rollback()

def _cleanup(session_maker):
    
    try:
        _session().close()
        session_maker.remove()
    finally:
        del _threadlocal.current_session
    
def _session():
    return _threadlocal.current_session.session if _session_exists() else None

def _current_count():
    return _threadlocal.current_session.count if _session_exists() else 0

def _should_commit():
    return _threadlocal.current_session.should_commit

def _session_exists():
    return hasattr(_threadlocal, 'current_session')

def _mark_as_rollback(session_maker):
    _threadlocal.current_session.rollback()
