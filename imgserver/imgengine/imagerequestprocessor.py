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
from __future__ import with_statement
import os
import os.path
import shutil
import time
import Image, ImageOps
from zope.interface import Interface, implements
from imgserver import domain
from imgserver import persistence
from imgserver import imgengine
from imgserver.domain.abstractimagemetadata import AbstractImageMetadata
from imgserver.domain.originalimagemetadata import OriginalImageMetadata
from imgserver.domain.derivedimagemetadata import DerivedImageMetadata
from imgserver.domain.imagemetadatarepository import DuplicateEntryException
from imgserver.resources.path import Path
from imgserver.resources import flatpathgenerator
from imgserver.resources.flatpathgenerator import FlatPathGenerator
from imgserver.resources.pathgenerator import PathGenerator
from imgserver.imgengine.deleteimagescommand import DeleteImagesCommand

LOCK_MAX_RETRIES = 10
LOCK_WAIT_SECONDS = 1
        
class IImageRequestProcessor(Interface):
    """ Processes ImageRequest objects and does the required work to prepare the images """
    
    def get_original_image_path(self, item_id):
        """@return: the relative path of the original image that has the given item_id 
        @rtype: str
        @raise ItemDoesNotExistError: if item_id does not exist"""
        
    def save_file_to_repository(self, file, image_id):
        """ save the given file to the image server repository. 
        It will then be available for transformations
        @param file: either a filename or a file-like object 
        that is opened in binary mode
        """
    
    def prepare_transformation(self, transformationRequest):
        """ Takes an ImageRequest and prepare the output for it. 
        Updates the database so that it is in sync with the filesystem
        @return: the path to the generated file (relative to the data directory)
        @raise ItemDoesNotExistError: if item_id does not exist
        @raise ImageProcessingException in case of any non-recoverable error 
        """
    
    def delete(self, item_id):
        """ Deletes the given item, and its associated item (in the case of an original 
        item that has derived items based on it)
        @raise ItemDoesNotExistError: if item_id does not exist
        """
    
    def cleanup_inconsistent_items(self):
        """ deletes the files and items whose status is not OK (startup cleanup)"""

class ItemDoesNotExistError(Exception):
    def __init__(self,item_id):
        super(ItemDoesNotExistError, self).__init__()
        self.item_id = item_id
 
class ImageRequestProcessor(object):
    implements(IImageRequestProcessor)
    
    def __init__(self, image_metadata_repository, schema_migrator, data_directory, drop_data=False):
        """ @param data_directory: the directory that this 
            ImageRequestProcessor will use for its work files """
        self.__data_directory = data_directory 
        self.__image_metadata_repository = image_metadata_repository
        self.__schema_migrator = schema_migrator
        self.__path_generator = PathGenerator(FlatPathGenerator(data_directory))
        
        if drop_data:
            self.__drop_data()
        
        self.__init_data()
        self.cleanup_inconsistent_items()

    def __wait_for_item_status_ok(self, pollingCallback):
        """ Wait for the status property of the object returned by pollingCallback() to be STATUS_OK
        It honors LOCK_MAX_RETRIES and LOCK_WAIT_SECONDS
        """
        item = pollingCallback()
        i = 0
        while i < LOCK_MAX_RETRIES and item is not None and item.status != domain.STATUS_OK:
            time.sleep(LOCK_WAIT_SECONDS)
            item = pollingCallback()
            i=i+1
    
    def __wait_for_original_image_metadata(self, item_id):
        """ Wait for the given original item to have a status of STATUS_OK """
        self.__wait_for_item_status_ok(lambda: self.__image_metadata_repository.find_original_image_metadata_by_id(item_id))
    
    def __required_original_image_metadata(self, item_id, original_image_metadata):
        if original_image_metadata is None:
            raise ItemDoesNotExistError(item_id)
                    
    def get_original_image_path(self, item_id):
        original_image_metadata = self.__image_metadata_repository.find_original_image_metadata_by_id(item_id)
        self.__required_original_image_metadata(item_id, original_image_metadata)
        self.__wait_for_original_image_metadata(item_id)
        return self.__path_generator.original_path(original_image_metadata).relative()
                               
    def save_file_to_repository(self, file, image_id):
        def filename_save_strategy(file, item):
            shutil.copyfile(file, self.__path_generator.original_path(item).absolute())
        
        def file_like_save_strategy(file, item):
            file.seek(0)
            with open(self.__path_generator.original_path(item).absolute(), "w+b") as out:
                shutil.copyfileobj(file, out)
                out.flush()

        imgengine.checkid(image_id)
        
        if type(file) == str:
            save = filename_save_strategy
        else:
            save = file_like_save_strategy
        
        # Check that the image is not broken
        try:
            img = Image.open(file)
            img.verify()
        except IOError, ex:
            raise imgengine.ImageFileNotRecognized(ex)
        
        item = OriginalImageMetadata(image_id, domain.STATUS_INCONSISTENT, img.size, img.format)

        try:
            # atomic creation
            self.__image_metadata_repository.create(item)
        except DuplicateEntryException, ex:
            raise imgengine.ImageIDAlreadyExistingException(item.id)
        else:
            try:
                save(file, item)
            except IOError, ex:
                raise imgengine.ImageProcessingException(ex)
        
        item.status = domain.STATUS_OK
        self.__image_metadata_repository.update(item)
            
    def prepare_transformation(self, transformationRequest):
        original_image_metadata = self.__image_metadata_repository.find_original_image_metadata_by_id(transformationRequest.image_id)
        self.__required_original_image_metadata(transformationRequest.image_id, original_image_metadata)
        
        self.__wait_for_original_image_metadata(transformationRequest.image_id)
        derived_image_metadata = DerivedImageMetadata(domain.STATUS_INCONSISTENT, transformationRequest.size, transformationRequest.target_format, original_image_metadata)
        
        cached_filename = self.__path_generator.derived_path(derived_image_metadata).absolute()
        relative_cached_filename = self.__path_generator.derived_path(derived_image_metadata).relative()

        # if image is already cached...
        if os.path.exists(cached_filename):
            return relative_cached_filename
        
        # otherwise, c'est parti to convert the stuff
        try:
            self.__image_metadata_repository.create(derived_image_metadata)
        except DuplicateEntryException :
            def find():
                return self.__image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format(original_image_metadata.id, transformationRequest.size, transformationRequest.target_format)
            self.__wait_for_item_status_ok(find)
            derived_image_metadata = find()
            
        try:
            img = Image.open(self.__path_generator.original_path(original_image_metadata).absolute())
        except IOError, ex: 
            raise imgengine.ImageProcessingException(ex)
        
        if transformationRequest.size == img.size and transformationRequest.target_format.upper() == img.format.upper():
            try:
                shutil.copyfile(self.__path_generator.original_path(original_image_metadata).absolute(), cached_filename)
            except IOError, ex:
                raise imgengine.ImageProcessingException(ex)
        else:   
            target_image = ImageOps.fit(image=img, 
                                        size=transformationRequest.size, 
                                        method=Image.ANTIALIAS,
                                        centering=(0.5,0.5)) 
            try:
                target_image.save(cached_filename)
            except IOError, ex:
                raise imgengine.ImageProcessingException(ex)
        
        derived_image_metadata.status = domain.STATUS_OK
        self.__image_metadata_repository.update(derived_image_metadata)
        
        return relative_cached_filename
    
    def cleanup_inconsistent_items(self):
        for command in [DeleteImagesCommand(self.__image_metadata_repository, 
                                       self.__schema_migrator.session_template(), 
                                       self.__path_generator,
                                       lambda: self.__image_metadata_repository.find_inconsistent_derived_image_metadatas()), 
                        DeleteImagesCommand(self.__image_metadata_repository, 
                                       self.__schema_migrator.session_template(), 
                                       self.__path_generator,
                                       lambda: self.__image_metadata_repository.find_inconsistent_original_image_metadatas())]:
            command.execute()
    
    def delete(self, item_id):
        def image_metadatas_to_delete():
            original_image_metadata = self.__image_metadata_repository.find_original_image_metadata_by_id(item_id)
            self.__required_original_image_metadata(item_id, original_image_metadata)
            return original_image_metadata.derived_items + [original_image_metadata]
        
        DeleteImagesCommand(self.__image_metadata_repository, 
                            self.__schema_migrator.session_template(), 
                            self.__path_generator,
                            lambda: self.__schema_migrator.session_template().do_with_session(image_metadatas_to_delete))
            
    def __drop_data(self):
        self.__schema_migrator.drop_all_tables()
        if os.path.exists(self.__data_directory):
            shutil.rmtree(self.__data_directory)
    
    def __init_directories(self):
        if not os.path.exists(self.__data_directory):
            os.makedirs(self.__data_directory)
        for directory in \
            [Path(self.__data_directory).append(flatpathgenerator.CACHE_DIRECTORY).absolute(), 
             Path(self.__data_directory).append(flatpathgenerator.ORIGINAL_DIRECTORY).absolute()]:
            if not os.path.exists(directory):
                os.makedirs(directory)    
    def __init_data(self):
        self.__init_directories()
        self.__schema_migrator.create_or_upgrade_schema()