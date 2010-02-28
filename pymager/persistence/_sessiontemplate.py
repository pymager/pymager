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
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session, backref #, eagerload

class SessionTemplate(object):
    """ Simple helper class akin to Spring-JDBC/Hibernate/ORM Template.
    It doesnt't commit nor releases resources if other do_with_session() calls are pending
    
    See http://www.sqlalchemy.org/trac/ticket/1084#comment:3 for suggestions on how to improve this
    without using a custom threadlocal variable
     """
    def __init__(self, sessionmaker):
        self.__sessionmaker = sessionmaker
        self.__local = threading.local()
        
    def do_with_session(self, session_callback):        
        session = self.__sessionmaker()
        self.__local.do_with_session_count = self.__local.do_with_session_count + 1 if hasattr(self.__local, 'do_with_session_count') and self.__local.do_with_session_count is not None else 1
        
        def cleanup_on_exception(f):
            try:
                return f()
            except Exception, ex:
                del self.__local.do_with_session_count
                try:
                    conn = session.connection().invalidate()
                except sqlalchemy.exceptions.InvalidRequestError:
                    # ignore the following exception that happens on windows... 
                    # InvalidRequestError("The transaction is inactive 
                    # due to a rollback in a subtransaction and should be closed")
                    #
                    pass
                except Exception:
                    pass
                #conn.close()
                session.rollback()
                session.close()
                self.__sessionmaker.remove()
                raise ex
        
        def do():
            o = session_callback(session)
            count = self.__local.do_with_session_count
            if count == 1:
                session.commit()
                session.close()
                self.__sessionmaker.remove()
                del self.__local.do_with_session_count
            else:
                self.__local.do_with_session_count = count - 1
            return o
        
        return cleanup_on_exception(do)
