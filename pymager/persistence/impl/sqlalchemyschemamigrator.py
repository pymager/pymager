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

import logging
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, Unicode, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session, backref #, eagerload
from zope.interface import Interface, implements
from pymager import domain
from pymager import persistence

log = logging.getLogger('persistence.schemamigrator')

class SqlAlchemySchemaMigrator(object):
    implements(persistence.SchemaMigrator)
    def __init__(self, engine, session_template):
        self.__engine = engine
        self.__metadata = MetaData()
        self.__template = session_template
        
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

        mapper(domain.AbstractImageMetadata, abstract_item, \
               polymorphic_on=abstract_item.c.type, \
               polymorphic_identity='ABSTRACT_ITEM', \
               column_prefix='_') 
        mapper(domain.OriginalImageMetadata, original_image_metadata, \
               inherits=domain.AbstractImageMetadata, \
               polymorphic_identity='ORIGINAL_ITEM', \
               column_prefix='_',
               properties={
                            'derived_image_metadatas' : relation(domain.DerivedImageMetadata,
                                                      primaryjoin=derived_image_metadata.c.original_image_metadata_id == original_image_metadata.c.id,
                                                      cascade='all',
                                                      backref='_original_image_metadata' 
                                                      #backref=backref('_originalItem', 
                                                      #                cascade="refresh-expire", 
                                                      #                primaryjoin=derived_image_metadata.c.original_image_metadata_id==original_image_metadata.c.id)
                                                      ) 
                           }) 
        mapper(domain.DerivedImageMetadata, derived_image_metadata,
               properties={ 
                           #'_originalItem' : relation(domain.OriginalImageMetadata, primaryjoin=derived_image_metadata.c.original_image_metadata_id==original_image_metadata.c.id, backref='derived_image_metadatas')
                           }, inherits=domain.AbstractImageMetadata , polymorphic_identity='DERIVED_ITEM', column_prefix='_')
    
    
    def drop_all_tables(self):
        self.__metadata.drop_all(self.__engine, checkfirst=True)
    
    def create_schema(self):
        log.info("Creating Database Schema")
        self.__metadata.create_all(self.__engine, checkfirst=True)
