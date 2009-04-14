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
from imgserver.domain.abstractitem import AbstractItem
from imgserver.domain.originalitem import OriginalItem
from imgserver.domain.deriveditem import DerivedItem
from imgserver.domain.itemrepository import DuplicateEntryException

CACHE_DIRECTORY = "cache"
ORIGINAL_DIRECTORY = "pictures"
FORMAT_EXTENSIONS = { "JPEG" : "jpg" }

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
        item that has derived items based on it)"""
    
    def cleanup_inconsistent_items(self):
        """ deletes the files and items whose status is not OK (startup cleanup)"""

class ItemDoesNotExistError(Exception):
    def __init__(self,item_id):
        super(ItemDoesNotExistError, self).__init__()
        self.item_id = item_id

class Path(object):
    def __init__(self, reference_directory, path_elements=[]):
        self.__reference_directory = reference_directory
        self.__path_elements = path_elements
    
    def absolute(self):
        return os.path.join(self.__reference_directory, *self.__path_elements)
    
    def relative(self):
        return os.path.join(*self.__path_elements)

    def append(self, path_element):
        return Path(self.__reference_directory, self.__path_elements + [path_element])
    
class PathGenerator(Interface):
    def original_path(self, original_item):
        """returns a Path object for the given original item"""
    
    def derived_path(self, derived_item):
        """ returns a Path object for the given derived item"""

class FlatPathGenerator(object):
    implements(PathGenerator)
    def __init__(self, data_directory):
        self.__data_directory = data_directory
    
    def __extension_for_format(self, format):
        return FORMAT_EXTENSIONS[format.upper()] if FORMAT_EXTENSIONS.__contains__(format.upper()) else format.lower()
    
    def original_path(self, original_item):
        return Path(self.__data_directory).append(ORIGINAL_DIRECTORY).append('%s.%s' % (original_item.id, self.__extension_for_format(original_item.format)))
    
    def derived_path(self, derived_item):
        return Path(self.__data_directory).append(CACHE_DIRECTORY).append('%s-%sx%s.%s' % (derived_item.original_item.id, derived_item.size[0], derived_item.size[1],self.__extension_for_format(derived_item.format)))
    
class ImageRequestProcessor(object):
    implements(IImageRequestProcessor)
    
    def __init__(self, item_repository, schema_migrator, data_directory, drop_data=False):
        """ @param data_directory: the directory that this 
            ImageRequestProcessor will use for its work files """
        self.__data_directory = data_directory 
        self.__item_repository = item_repository
        self.__schema_migrator = schema_migrator
        self.__path_generator = PathGenerator(FlatPathGenerator(data_directory))
        self.__original_items_directory = Path(data_directory,[CACHE_DIRECTORY])
        self.__derived_items_directory = Path(data_directory, [ORIGINAL_DIRECTORY])
        
        if drop_data:
            self.__drop_data()
        
        self.__init_data()
        self.cleanup_inconsistent_items()
        
    def __extensionForFormat(self, format):
        return FORMAT_EXTENSIONS[format.upper()] if FORMAT_EXTENSIONS.__contains__(format.upper()) else format.lower()

    def __waitForItemStatusOk(self, pollingCallback):
        """ Wait for the status property of the object returned by pollingCallback() to be STATUS_OK
        It honors LOCK_MAX_RETRIES and LOCK_WAIT_SECONDS
        """
        item = pollingCallback()
        i = 0
        while i < LOCK_MAX_RETRIES and item is not None and item.status != domain.STATUS_OK:
            time.sleep(LOCK_WAIT_SECONDS)
            item = pollingCallback()
            i=i+1
    
    def __wait_for_original_item(self, item_id):
        """ Wait for the given original item to have a status of STATUS_OK """
        self.__waitForItemStatusOk(lambda: self.__item_repository.find_original_item_by_id(item_id))
    
    def __required_original_item(self, item_id, original_item):
        if original_item is None:
            raise ItemDoesNotExistError(item_id)
    
    def originalImageExists(self, item_id):
        original_item = self.__item_repository.find_original_item_by_id(item_id)
        return original_item is not None
                
    def get_original_image_path(self, item_id):
        original_item = self.__item_repository.find_original_item_by_id(item_id)
        self.__required_original_item(item_id, original_item)
        self.__wait_for_original_item(item_id)
        return self.__path_generator.original_path(original_item).relative()
                               
    def save_file_to_repository(self, file, image_id):
        def filenameSaveStrategy(file, item):
            shutil.copyfile(file, self.__path_generator.original_path(item).absolute())
        
        def fileLikeSaveStrategy(file, item):
            file.seek(0)
            with open(self.__path_generator.original_path(item).absolute(), "w+b") as out:
                shutil.copyfileobj(file, out)
                out.flush()

        imgengine.checkid(image_id)
        
        if type(file) == str:
            save = filenameSaveStrategy
        else:
            save = fileLikeSaveStrategy
        
        # Check that the image is not broken
        try:
            img = Image.open(file)
            img.verify()
        except IOError, ex:
            raise imgengine.ImageFileNotRecognized(ex)
        
        item = OriginalItem(image_id, domain.STATUS_INCONSISTENT, img.size, img.format)

        try:
            # atomic creation
            self.__item_repository.create(item)
        except DuplicateEntryException, ex:
            raise imgengine.ImageIDAlreadyExistingException(item.id)
        else:
            try:
                save(file, item)
            except IOError, ex:
                raise imgengine.ImageProcessingException(ex)
        
        item.status = domain.STATUS_OK
        self.__item_repository.update(item)
            
    def prepare_transformation(self, transformationRequest):
        original_item = self.__item_repository.find_original_item_by_id(transformationRequest.image_id)
        self.__required_original_item(transformationRequest.image_id, original_item)
        
        self.__wait_for_original_item(transformationRequest.image_id)
        derived_item = DerivedItem(domain.STATUS_INCONSISTENT, transformationRequest.size, transformationRequest.target_format, original_item)
        
        cached_filename = self.__path_generator.derived_path(derived_item).absolute()
        relative_cached_filename = self.__path_generator.derived_path(derived_item).relative()

        # if image is already cached...
        if os.path.exists(cached_filename):
            return relative_cached_filename
        
        # otherwise, c'est parti to convert the stuff
        try:
            self.__item_repository.create(derived_item)
        except DuplicateEntryException :
            def find():
                return self.__item_repository.find_derived_item_by_original_item_id_size_and_format(original_item.id, transformationRequest.size, transformationRequest.target_format)
            self.__waitForItemStatusOk(find)
            derived_item = find()
            
        try:
            img = Image.open(self.__path_generator.original_path(original_item).absolute())
        except IOError, ex: 
            raise imgengine.ImageProcessingException(ex)
        
        if transformationRequest.size == img.size and transformationRequest.target_format.upper() == img.format.upper():
            try:
                shutil.copyfile(self.__path_generator.original_path(original_item).absolute(), cached_filename)
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
        
        derived_item.status = domain.STATUS_OK
        self.__item_repository.update(derived_item)
        
        return relative_cached_filename
    
    def cleanup_inconsistent_items(self):
        def cleanup_in_session(fetch_items, delete_file):
            items = fetch_items()
            for i in items:
                delete_file(i)
                self.__item_repository.delete(i)
            
        def main_loop(has_more_items, fetch_items, delete_file):
            def callback(session):
                cleanup_in_session(fetch_items, delete_file)
            while has_more_items():
                self.__schema_migrator.session_template().do_with_session(callback)
        
        def cleanup_derived_items():
            def delete_file(item):
                os.remove(self.__path_generator.derived_path(item).absolute())
            main_loop(lambda: len(self.__item_repository.find_inconsistent_derived_items(1)) > 0,
                      lambda: self.__item_repository.find_inconsistent_derived_items(), 
                      delete_file)
        
        def cleanup_original_items():
            def delete_file(item):
                os.remove(self.__path_generator.original_path(item).absolute())
            main_loop(lambda: len(self.__item_repository.find_inconsistent_original_items(1)) > 0,
                      lambda: self.__item_repository.find_inconsistent_original_items(), 
                      delete_file)
            
        cleanup_derived_items()
        cleanup_original_items()
    
    def delete(self, item_id):
        pass
            
    def __drop_data(self):
        self.__schema_migrator.drop_all_tables()
        if os.path.exists(self.__data_directory):
            shutil.rmtree(self.__data_directory)
    
    def __init_directories(self):
        if not os.path.exists(self.__data_directory):
            os.makedirs(self.__data_directory)
        for directory in \
            [self.__original_items_directory.absolute(), self.__derived_items_directory.absolute()]:
            if not os.path.exists(directory):
                os.makedirs(directory)    
    def __init_data(self):
        self.__init_directories()
        self.__schema_migrator.create_or_upgrade_schema()