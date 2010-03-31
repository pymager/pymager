"""
   Copyright 2010 Sami Dalouche

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
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
            raise