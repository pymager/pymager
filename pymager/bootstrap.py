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

import os
import logging
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session, backref #, eagerload

from pymager import imgengine
from pymager import persistence
from pymager import domain
from pymager import resources
from pymager.imgengine import image_transformation_security_decorator
from pymager.imgengine.impl.defaultimagerequestprocessor import DefaultImageRequestProcessor
from pymager.resources.impl.pilimageformatmapper import PilImageFormatMapper
from pymager.resources.impl.flatpathgenerator import FlatPathGenerator
from pymager.resources.impl.nestedpathgenerator import NestedPathGenerator

class ServiceConfiguration(object):
    def __init__(self, data_directory, dburi, allowed_sizes, dev_mode):
        self.data_directory = data_directory
        self.dburi = dburi
        self.allowed_sizes = allowed_sizes
        self.dev_mode = dev_mode

class ImageServerFactory(object):
    def __init__(self, config):
        super(ImageServerFactory, self)
        self._schema_migrator = None
        self._image_metadata_repository = None
        self._image_processor = None
        self._config = config
        self._engine = None
        self._session_template = None
        self._sessionmaker = None
        self._image_format_mapper = None
        self._path_generator = None

    def get_schema_migrator(self):
        return self._schema_migrator

    def get_image_metadata_repository(self):
        return self._image_metadata_repository

    def get_image_processor(self):
        return self._image_processor
    
    def get_engine(self):
        return self._engine
    
    def get_sessionmaker(self):
        return self._sessionmaker
    
    def get_session_template(self):
        return self._session_template
    
    def get_image_format_mapper(self):
        return self._image_format_mapper
    
    def get_path_generator(self):
        return self._path_generator
    
    def create_image_server(self):
        configure_logging()
        # 1. make sure to initialize the persistence module
        self._engine = create_engine(self._config.dburi, encoding='utf-8', echo=False, echo_pool=False) # strategy='threadlocal'
        self._sessionmaker = scoped_session(sessionmaker(bind=self._engine, autoflush=True, autocommit=False))
        persistence.init(sessionmaker=self._sessionmaker)
        
        # 2. We should then be able to use the persistence module
        from pymager.persistence.impl.sqlalchemyschemamigrator import SqlAlchemySchemaMigrator
        from pymager.persistence.impl.sqlalchemyimagemetadatarepository import SqlAlchemyImageMetadataRepository
        
        self._image_format_mapper = resources.ImageFormatMapper(PilImageFormatMapper())
        self._path_generator = resources.PathGenerator(NestedPathGenerator(self._image_format_mapper, self._config.data_directory))
        self._session_template = persistence.SessionTemplate(self._sessionmaker)
        self._schema_migrator = persistence.SchemaMigrator(SqlAlchemySchemaMigrator(self._engine, self._session_template))
        self._image_metadata_repository = domain.ImageMetadataRepository(SqlAlchemyImageMetadataRepository(self._session_template))
        self._image_processor = imgengine.ImageRequestProcessor(DefaultImageRequestProcessor(self._image_metadata_repository, self._path_generator, self._image_format_mapper, self._schema_migrator, self._config.data_directory, self._session_template, self._config.dev_mode))
        self._image_processor.prepare_transformation = image_transformation_security_decorator.image_transformation_security_decorator(self._config.allowed_sizes)(self._image_processor.prepare_transformation)
        
        
        return self._image_processor
    
    schema_migrator = property(get_schema_migrator, None, None, "PersistenceProvider's Docstring")
    image_metadata_repository = property(get_image_metadata_repository, None, None, "domain.ImageMetadataRepository's Docstring")
    image_processor = property(get_image_processor, None, None, "ImageProcessor's Docstring")
    engine = property(get_engine, None, None, "ImageProcessor's Docstring")
    sessionmaker = property(get_sessionmaker, None, None, "ImageProcessor's Docstring")
    session_template = property(get_session_template, None, None, "ImageProcessor's Docstring")
    image_format_mapper = property(get_image_format_mapper, None, None, "Image Format Mapper")
    path_generator = property(get_path_generator, None, None, "Path Generator")

def configure_logging():
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
