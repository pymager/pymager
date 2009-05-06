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
import os
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session,backref #, eagerload

from imgserver import imgengine
from imgserver import persistence
from imgserver import domain
from imgserver import resources
from imgserver.imgengine import image_transformation_security_decorator
from imgserver.imgengine.impl.defaultimagerequestprocessor import DefaultImageRequestProcessor
from imgserver.persistence.impl.sqlalchemyschemamigrator import SqlAlchemySchemaMigrator
from imgserver.persistence.impl.sqlalchemyimagemetadatarepository import SqlAlchemyImageMetadataRepository
from imgserver.resources.impl.pilimageformatmapper import PilImageFormatMapper
from imgserver.resources.impl.flatpathgenerator import FlatPathGenerator
from imgserver.resources.impl.nestedpathgenerator import NestedPathGenerator

class ServiceConfiguration(object):
    def __init__(self, data_directory, dburi, allowed_sizes, dev_mode):
        self.data_directory = data_directory
        self.dburi = dburi
        self.allowed_sizes = allowed_sizes
        self.dev_mode = dev_mode

class ImageServerFactory(object):
    def __init__(self, config):
        super(ImageServerFactory, self)
        self.__schema_migrator = None
        self.__image_metadata_repository = None
        self.__image_processor = None
        self.__config = config
        self.__engine = None
        self.__session_template = None
        self.__sessionmaker = None
        self.__image_format_mapper = None
        self.__path_generator = None

    def get_schema_migrator(self):
        return self.__schema_migrator

    def get_image_metadata_repository(self):
        return self.__image_metadata_repository

    def get_image_processor(self):
        return self.__image_processor
    
    def get_engine(self):
        return self.__engine
    
    def get_sessionmaker(self):
        return self.__sessionmaker
    
    def get_session_template(self):
        return self.__session_template
    
    def get_image_format_mapper(self):
        return self.__image_format_mapper
    
    def get_path_generator(self):
        return self.__path_generator
    
    def create_image_server(self):
        self.__image_format_mapper = resources.ImageFormatMapper(PilImageFormatMapper())
        self.__path_generator = resources.PathGenerator(NestedPathGenerator(self.__image_format_mapper, self.__config.data_directory))
        
        self.__engine = create_engine(self.__config.dburi, encoding='utf-8', echo=False, echo_pool=False) # strategy='threadlocal'
        self.__sessionmaker = scoped_session(sessionmaker(bind=self.__engine, autoflush=True, transactional=True))
        self.__session_template = persistence.SessionTemplate(self.__sessionmaker)
        
        self.__schema_migrator = persistence.SchemaMigrator(SqlAlchemySchemaMigrator(self.__engine, self.__session_template))
        
        self.__image_metadata_repository = domain.ImageMetadataRepository(SqlAlchemyImageMetadataRepository(self.__session_template))
        self.__image_processor = imgengine.ImageRequestProcessor(DefaultImageRequestProcessor(self.__image_metadata_repository, self.__path_generator, self.__image_format_mapper, self.__schema_migrator, self.__config.data_directory, self.__session_template, self.__config.dev_mode))
        self.__image_processor.prepare_transformation =  image_transformation_security_decorator.image_transformation_security_decorator(self.__config.allowed_sizes)(self.__image_processor.prepare_transformation)
        
        return self.__image_processor
    
    schema_migrator = property(get_schema_migrator, None, None, "PersistenceProvider's Docstring")
    image_metadata_repository = property(get_image_metadata_repository, None, None, "domain.ImageMetadataRepository's Docstring")
    image_processor = property(get_image_processor, None, None, "ImageProcessor's Docstring")
    engine = property(get_engine, None, None, "ImageProcessor's Docstring")
    sessionmaker = property(get_sessionmaker, None, None, "ImageProcessor's Docstring")
    session_template = property(get_session_template, None, None, "ImageProcessor's Docstring")
    image_format_mapper = property(get_image_format_mapper, None, None, "Image Format Mapper")
    path_generator = property(get_path_generator, None, None, "Path Generator")