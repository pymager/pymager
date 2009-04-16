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
import logging
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session,backref #, eagerload
from zope.interface import Interface, implements
from imgserver import domain
from imgserver.domain.abstractimagemetadata import AbstractImageMetadata
from imgserver.domain.originalimagemetadata import OriginalImageMetadata
from imgserver.domain.derivedimagemetadata import DerivedImageMetadata
from imgserver.persistence.schemamigrator import SchemaMigrator

log = logging.getLogger('persistence.persistenceprovider')

class Version(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class SqlAlchemySchemaMigrator(object):
    implements(SchemaMigrator)
    def __init__(self, engine, session_template):
        self.__engine = engine
        self.__metadata = MetaData()
        self.__template = session_template
        
        version = Table('version', self.__metadata,
            Column('name', String(255), primary_key=True),
            Column('value', Integer)
        )
        
        abstract_item = Table('abstract_item', self.__metadata,
            Column('id', String(255), primary_key=True),
            Column('status', String(255), index=True, nullable=False),
            Column('last_status_change_date', DateTime, index=True, nullable=False),
            Column('width', Integer, index=True, nullable=False),
            Column('height', Integer, index=True, nullable=False),
            Column('format', String(255), index=True, nullable=False),
            Column('type', String(255), nullable=False)
        )
        
        original_image_metadata = Table('original_image_metadata', self.__metadata,  
            Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True)
        )
        
        derived_image_metadata = Table('derived_image_metadata', self.__metadata,
            Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True),
            Column('original_image_metadata_id', String(255), ForeignKey('original_image_metadata.id', ondelete="CASCADE"))
        )

        mapper(AbstractImageMetadata, abstract_item, \
               polymorphic_on=abstract_item.c.type, \
               polymorphic_identity='ABSTRACT_ITEM', \
               column_prefix='_') 
        mapper(OriginalImageMetadata, original_image_metadata, \
               inherits=AbstractImageMetadata, \
               polymorphic_identity='ORIGINAL_ITEM', \
               column_prefix='_',
               properties={
                            'derived_image_metadatas' : relation(DerivedImageMetadata, 
                                                      primaryjoin=derived_image_metadata.c.original_image_metadata_id==original_image_metadata.c.id,
                                                      cascade='all',
                                                      backref='_original_image_metadata' 
                                                      #backref=backref('_originalItem', 
                                                      #                cascade="refresh-expire", 
                                                      #                primaryjoin=derived_image_metadata.c.original_image_metadata_id==original_image_metadata.c.id)
                                                      ) 
                           }) 
        mapper(DerivedImageMetadata, derived_image_metadata, 
               properties={ 
                           #'_originalItem' : relation(OriginalImageMetadata, primaryjoin=derived_image_metadata.c.original_image_metadata_id==original_image_metadata.c.id, backref='derived_image_metadatas')
                           }, inherits=AbstractImageMetadata , polymorphic_identity='DERIVED_ITEM', column_prefix='_')
        mapper(Version, version)
    
    
    def drop_all_tables(self):
        self.__metadata.drop_all(self.__engine)
    
    def create_or_upgrade_schema(self):
        def get_version(session):
            schema_version = None
            try:
                schema_version = session.query(Version)\
                                    .filter(Version.name=='schema')\
                                    .first()
                schema_version = schema_version if schema_version is not None else Version('schema', 0)
            except sqlalchemy.exceptions.OperationalError:
                schema_version = Version('schema', 0)
            except sqlalchemy.exceptions.ProgrammingError:
                schema_version = Version('schema', 0)  
            return schema_version
        
        def store_latest_version(session):
            version = get_version(session)
            version.value = 1
            session.save_or_update(version)
        
        schema_version = self.__template.do_with_session(get_version)
        if schema_version.value == 0:
            log.info('Upgrading Database Schema...')
            self.__metadata.create_all(self.__engine)
            self.__template.do_with_session(store_latest_version)
        elif schema_version.value == 1:
            log.info('Database Schema already up to date')
        else:
            raise NoUpgradeScriptError(schema_version)
