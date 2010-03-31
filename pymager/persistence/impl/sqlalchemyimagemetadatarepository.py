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


from zope.interface import Interface, implements
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session, backref #, eagerload
from sqlalchemy.orm import exc
import logging
import threading
from pymager import persistence
from pymager import domain

log = logging.getLogger('domain.imagemetadatarepository')

class SqlAlchemyImageMetadataRepository(object):
    implements(domain.ImageMetadataRepository)
    
    def __init__(self, session_template):
        self.__template = session_template
    
    def find_original_image_metadata_by_id(self, image_id):
        def callback(session):
            return session.query(domain.OriginalImageMetadata)\
                .filter(domain.OriginalImageMetadata._id == image_id)\
                .first()
        return self.__template.do_with_session(callback)

    def find_inconsistent_original_image_metadatas(self, maxResults=100):
        def callback(session):
            return session.query(domain.OriginalImageMetadata)\
                .filter(domain.AbstractImageMetadata._status == domain.STATUS_INCONSISTENT)\
                .limit(maxResults).all()
        return self.__template.do_with_session(callback)
    
    def find_inconsistent_derived_image_metadatas(self, maxResults=100):
        def callback(session):
            return session.query(domain.DerivedImageMetadata)\
                .filter(domain.AbstractImageMetadata._status == domain.STATUS_INCONSISTENT)\
                .limit(maxResults).all()
        return self.__template.do_with_session(callback)
    
    def find_derived_image_metadata_by_original_image_metadata_id_size_and_format(self, image_id, size, format):
        def callback(session):
            o = session.query(domain.DerivedImageMetadata)\
                    .filter_by(_width=size[0])\
                    .filter_by(_height=size[1])\
                    .filter_by(_format=format)\
                    .join('_original_image_metadata', aliased=True)\
                    .filter_by(_id=image_id)\
                    .first()
            # FIXME: http://www.sqlalchemy.org/trac/ticket/1082
            (getattr(o, '_original_image_metadata') if hasattr(o, '_original_image_metadata') else (lambda: None))
            return o
        return self.__template.do_with_session(callback)
    
    def add(self, item):
        def callback(session):
            session.add(item)
            session.flush()
        try:
            self.__template.do_with_session(callback)
        except sqlalchemy.exc.IntegrityError as e: 
            raise domain.DuplicateEntryException(item.id)
        except exc.FlushError as e:
            raise domain.DuplicateEntryException(item.id)
    
    def delete(self, item):
        def callback(session):
            session.refresh(item)
            session.delete(item)
        self.__template.do_with_session(callback)
