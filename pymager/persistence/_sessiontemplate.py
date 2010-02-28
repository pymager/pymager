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
from pymager.persistence import _transaction

class SessionTemplate(object):
    """ Simple helper class akin to Spring-JDBC/Hibernate/ORM Template.
    It doesnt't commit nor releases resources if other do_with_session() calls are pending
    
    See http://www.sqlalchemy.org/trac/ticket/1084#comment:3 for suggestions on how to improve this
    without using a custom threadlocal variable
     """
    def __init__(self, sessionmaker):
        self.__sessionmaker = sessionmaker
        
    def do_with_session(self, session_callback):        
        session = _transaction.begin_scope(self.__sessionmaker)
        
        def do():
            result = session_callback(session)
            _transaction.end_scope(self.__sessionmaker)
            return result
        
        return self._do_execute(do)

    def _do_execute(self,f):
        try:
            return f()
        except Exception as ex:
            _transaction.rollback(self.__sessionmaker)
            raise ex