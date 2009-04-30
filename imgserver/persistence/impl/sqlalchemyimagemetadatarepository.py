"""
    ImgServer RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of ImgServer.

    ImgServer is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ImgServer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with ImgServer.  If not, see <http://www.gnu.org/licenses/>.
"""

from zope.interface import Interface, implements
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session,backref #, eagerload
import logging
import threading
from imgserver import persistence
from imgserver import domain

log = logging.getLogger('domain.imagemetadatarepository')

class SqlAlchemyImageMetadataRepository(object):
    implements(domain.ImageMetadataRepository)
    
    def __init__(self, session_template):
        self.__template = session_template
    
    def find_original_image_metadata_by_id(self, image_id):
        def callback(session):
            return session.query(domain.OriginalImageMetadata)\
                .filter(domain.OriginalImageMetadata._id==image_id)\
                .first()
        return self.__template.do_with_session(callback)

    def find_inconsistent_original_image_metadatas(self, maxResults=100):
        def callback(session):
            return session.query(domain.OriginalImageMetadata)\
                .filter(domain.AbstractImageMetadata._status==domain.STATUS_INCONSISTENT)\
                .limit(maxResults).all()
        return self.__template.do_with_session(callback)
    
    def find_inconsistent_derived_image_metadatas(self, maxResults=100):
        def callback(session):
            return session.query(domain.DerivedImageMetadata)\
                .filter(domain.AbstractImageMetadata._status==domain.STATUS_INCONSISTENT)\
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
    
    def create(self, item):
        def callback(session):
            session.save(item)
        try:
            self.__template.do_with_session(callback)
        except sqlalchemy.exceptions.IntegrityError, ex: 
            raise domain.DuplicateEntryException, item.id
    
    def update(self, item):
        def callback(session):
            session.save_or_update(item)
        try:
            self.__template.do_with_session(callback)
        except sqlalchemy.exceptions.IntegrityError: 
            raise domain.DuplicateEntryException, item.id
    
    def delete(self, item):
        def callback(session):
            session.refresh(item)
            session.delete(item)
        self.__template.do_with_session(callback)
