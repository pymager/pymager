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

from __future__ import with_statement
import os
import os.path
import shutil
import time
import Image, ImageOps
import logging
from zope.interface import Interface, implements
from pymager import tx
from pymager import domain
from pymager import persistence
from pymager import resources
from pymager import imgengine
from pymager.imgengine._deleteimagescommand import DeleteImagesCommand
from pymager.imgengine._imagerequestprocessor import ImageRequestProcessor
from pymager.resources.impl import flatpathgenerator

logger = logging.getLogger("imgengine.imagerequestprocessor")

LOCK_MAX_RETRIES = 10
LOCK_WAIT_SECONDS = 1

class DefaultImageRequestProcessor(object):
    implements(ImageRequestProcessor)
    
    def __init__(self, image_metadata_repository, path_generator, image_format_mapper, schema_migrator, data_directory, session_template, dev_mode=False):
        """ @param data_directory: the directory that this 
            ImageRequestProcessor will use for its work files """
        self._data_directory = data_directory 
        self._image_metadata_repository = domain.ImageMetadataRepository(image_metadata_repository)
        self._image_format_mapper = resources.ImageFormatMapper(image_format_mapper)
        self._schema_migrator = persistence.SchemaMigrator(schema_migrator)
        self._path_generator = resources.PathGenerator(path_generator)
        self._session_template = session_template
        self._dev_mode = dev_mode
        
        if self._dev_mode:
            self._drop_data()
        
        self._init_data()
        self.cleanup_inconsistent_items()
    
    @tx.transactional
    def _wait_for_item_status_ok(self, pollingCallback):
        """ Wait for the status property of the object returned by pollingCallback() to be STATUS_OK
        It honors LOCK_MAX_RETRIES and LOCK_WAIT_SECONDS
        """
        item = pollingCallback()
        i = 0
        while i < LOCK_MAX_RETRIES and item is not None and item.status != domain.STATUS_OK:
            time.sleep(LOCK_WAIT_SECONDS)
            item = pollingCallback()
            i = i + 1
        if i == LOCK_MAX_RETRIES:
            raise imgengine.ImageProcessingException('Item seems to be locked forever')
    
    def _wait_for_original_image_metadata(self, image_id):
        """ Wait for the given original item to have a status of STATUS_OK """
        self._wait_for_item_status_ok(lambda: self._image_metadata_repository.find_original_image_metadata_by_id(image_id))
    
    def _required_original_image_metadata(self, image_id, original_image_metadata):
        if original_image_metadata is None:
            raise imgengine.ImageMetadataNotFoundException(image_id)
    
    @tx.transactional                
    def get_original_image_path(self, image_id):
        logger.debug("get_original_image_path")
        original_image_metadata = self._image_metadata_repository.find_original_image_metadata_by_id(image_id)
        self._required_original_image_metadata(image_id, original_image_metadata)
        self._wait_for_original_image_metadata(image_id)
        return self._path_generator.original_path(original_image_metadata).relative()
    
    @tx.transactional                           
    def save_file_to_repository(self, file, image_id):
        def filename_save_strategy(file, item):
            shutil.copyfile(file, self._path_generator.original_path(item).absolute())
        
        def file_like_save_strategy(file, item):
            file.seek(0)
            with open(self._path_generator.original_path(item).absolute(), "w+b") as out:
                shutil.copyfileobj(file, out)
                out.flush()

        if type(file) == str:
            save = filename_save_strategy
        else:
            save = file_like_save_strategy
        
        # Check that the image is not broken
        try:
            img = Image.open(file)
            img.verify()
        except IOError, ex:
            raise imgengine.ImageStreamNotRecognizedException(ex)
        
        item = domain.OriginalImageMetadata(image_id, domain.STATUS_INCONSISTENT, img.size, img.format)

        try:
            # atomic creation
            self._image_metadata_repository.add(item)
        except domain.DuplicateEntryException, ex:
            raise imgengine.ImageIDAlreadyExistsException(item.id)
        else:
            try:
                image_directory = self._path_generator.original_path(item).parent_directory().absolute()
                if not os.path.exists(image_directory):
                    os.makedirs(image_directory)
                save(file, item)
            except IOError, ex:
                raise imgengine.ImageProcessingException(ex)
        
        item.status = domain.STATUS_OK
    
    @tx.transactional        
    def prepare_transformation(self, transformationRequest):
        logging.debug("prepare transformation: %s" % (transformationRequest,))
        original_image_metadata = self._image_metadata_repository.find_original_image_metadata_by_id(transformationRequest.image_id)
        self._required_original_image_metadata(transformationRequest.image_id, original_image_metadata)
        
        self._wait_for_original_image_metadata(transformationRequest.image_id)
        derived_image_metadata = domain.DerivedImageMetadata(domain.STATUS_INCONSISTENT, transformationRequest.size, transformationRequest.target_format, original_image_metadata)
        
        cached_filename = self._path_generator.derived_path(derived_image_metadata).absolute()
        relative_cached_filename = self._path_generator.derived_path(derived_image_metadata).relative()

        logger.debug("Checks cache for existing image")
        if os.path.exists(cached_filename):
            logger.debug("Already exists in cache: %s " %(relative_cached_filename,))
            def expunge_callback(session):
                session.expunge_all()
            self._session_template.do_with_session(expunge_callback)
            return relative_cached_filename
        
        logger.debug("Add repo metadata for derived image")
        try:
            self._image_metadata_repository.add(derived_image_metadata)
        except domain.DuplicateEntryException :
            def find():
                return self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format(transformationRequest.image_id, transformationRequest.size, transformationRequest.target_format)
            self._wait_for_item_status_ok(find)
            derived_image_metadata = find()

        logger.debug("Checks that image format is supported")        
        try:
            img = Image.open(self._path_generator.original_path(original_image_metadata).absolute())
        except IOError, ex: 
            raise imgengine.ImageProcessingException(ex)
        
        logger.debug("Add derived image to filesystem")
        if transformationRequest.size == img.size and transformationRequest.target_format.upper() == img.format.upper():
            try:
                shutil.copyfile(self._path_generator.original_path(original_image_metadata).absolute(), cached_filename)
            except IOError, ex:
                raise imgengine.ImageProcessingException(ex)
        else:   
            target_image = ImageOps.fit(image=img,
                                        size=transformationRequest.size,
                                        method=Image.ANTIALIAS,
                                        centering=(0.5, 0.5)) 
            try:
                cached_filename_directory = self._path_generator.derived_path(derived_image_metadata).parent_directory().absolute()
                if not os.path.exists(cached_filename_directory):
                    os.makedirs(cached_filename_directory)
                target_image.save(cached_filename)
            except IOError, ex:
                raise imgengine.ImageProcessingException(ex)
        
        derived_image_metadata.status = domain.STATUS_OK
        
        return relative_cached_filename
    
    @tx.transactional
    def cleanup_inconsistent_items(self):
        for command in [DeleteImagesCommand(self._image_metadata_repository,
                                       self._session_template,
                                       self._path_generator,
                                       lambda: self._image_metadata_repository.find_inconsistent_derived_image_metadatas()),
                        DeleteImagesCommand(self._image_metadata_repository,
                                       self._session_template,
                                       self._path_generator,
                                       lambda: self._image_metadata_repository.find_inconsistent_original_image_metadatas())]:
            command.execute()
    
    @tx.transactional
    def delete(self, image_id):
        def image_metadatas_to_delete():
            original_image_metadata = self._image_metadata_repository.find_original_image_metadata_by_id(image_id)
            self._required_original_image_metadata(image_id, original_image_metadata)
            return list(original_image_metadata.derived_image_metadatas) + [original_image_metadata]
        
        DeleteImagesCommand(self._image_metadata_repository,
                            self._session_template,
                            self._path_generator,
                            lambda: image_metadatas_to_delete()).execute()
            
    def _drop_data(self):
        self._schema_migrator.drop_all_tables()
        if os.path.exists(self._data_directory):
            shutil.rmtree(self._data_directory)
    
    def _init_directories(self):
        if not os.path.exists(self._data_directory):
            os.makedirs(self._data_directory)
        for directory in \
            [resources.Path(self._data_directory).append(flatpathgenerator.CACHE_DIRECTORY).absolute(),
             resources.Path(self._data_directory).append(flatpathgenerator.ORIGINAL_DIRECTORY).absolute()]:
            if not os.path.exists(directory):
                os.makedirs(directory)    
    def _init_data(self):
        #self._init_directories()
        if self._dev_mode:
            self._schema_migrator.drop_all_tables()
            self._schema_migrator.create_schema()
