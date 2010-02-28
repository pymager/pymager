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
import sqlalchemy

local = threading.local()

class BoundSession(object):
    def __init__(self, session, count=0):
        assert count >= 0
        self.session = session
        self.count = count
    
    def increment(self):
        self.count=self.count+1
    
    def decrement(self):
        self.count=self.count -1

def begin_scope(session_maker):
    bound_session = local.current_session if _session_exists() else BoundSession(session_maker())
    bound_session.increment()
    local.current_session = bound_session
    return bound_session.session

def end_scope(session_maker):
    if _current_count() == 1:
        try:
            _session().commit()
        finally:
            _cleanup(session_maker)
    else:
        local.current_session.decrement()

def rollback(session_maker):
    if not _session_exists():
        return
    
    try:
        conn = _session().connection().invalidate()
    except sqlalchemy.exceptions.InvalidRequestError:
        # ignore the following exception that happens on windows... 
        # InvalidRequestError("The transaction is inactive 
        # due to a rollback in a subtransaction and should be closed")
        #
        pass
    except Exception:
        pass
    #conn.close()
    try:
        _session().rollback()
    finally:
        _cleanup(session_maker)

def _cleanup(session_maker):
    
    try:
        _session().close()
        session_maker.remove()
    finally:
        del local.current_session
    
def _session():
    return local.current_session.session if _session_exists() else None

def _current_count():
    return local.current_session.count if _session_exists() else 0

def _session_exists():
    return hasattr(local, 'current_session')