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
import unittest
import os
import time
import random
import exceptions
from threading import Thread
from pkg_resources import resource_filename
from pymager import imgengine, domain
from tests.pymagertests.abstractintegrationtestcase import AbstractIntegrationTestCase

#JPG_SAMPLE_IMAGE_FILENAME = os.path.join('..', '..', 'samples', 'sami.jpg')
#BROKEN_IMAGE_FILENAME = os.path.join('..', '..', 'samples', 'brokenImage.jpg')
JPG_SAMPLE_IMAGE_FILENAME = resource_filename('pymager.samples', 'sami.jpg')
BROKEN_IMAGE_FILENAME = resource_filename('pymager.samples', 'brokenImage.jpg')
JPG_SAMPLE_IMAGE_SIZE = (3264, 2448)

class ImageRequestProcessorTestCase(AbstractIntegrationTestCase):
    
    def onSetUp(self):
        self._image_metadata_repository = self._image_server_factory.image_metadata_repository
        self._schema_migrator = self._image_server_factory.schema_migrator
        self._template = self._image_server_factory.session_template
        self._image_format_mapper = self._image_server_factory.image_format_mapper
        self._path_generator = self._image_server_factory.path_generator
    
    def test_should_not_save_broken_image(self):
        try:
            self._image_server.save_file_to_repository(BROKEN_IMAGE_FILENAME, 'sampleId')
            self.fail()
        except imgengine.ImageStreamNotRecognizedException, ex:
            pass
    
    def test_should_not_save_image_with_existing_id(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        try:
            self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
            self.fail()    
        except imgengine.ImageIDAlreadyExistsException, ex:
            assert ex.image_id == 'sampleId'
    
    def test_saving_image_should_update_file_system_and_database(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        original_image_metadata = self._image_metadata_repository.find_original_image_metadata_by_id('sampleId')
        assert original_image_metadata is not None
        assert original_image_metadata.id == 'sampleId'
        assert original_image_metadata.format == domain.IMAGE_FORMAT_JPEG
        assert original_image_metadata.size == JPG_SAMPLE_IMAGE_SIZE
        assert original_image_metadata.status == domain.STATUS_OK
        
        self._original_image_should_exist(original_image_metadata)
    
    
    def test_save_image_should_accept_file_like_object_as_image_source(self):
        with open(JPG_SAMPLE_IMAGE_FILENAME, 'rb') as fobj:
            self._image_server.save_file_to_repository(fobj, 'sampleId')
            
        self._original_image_should_exist(self._image_metadata_repository.find_original_image_metadata_by_id('sampleId'))
    
    def test_should_not_prepare_transformation_when_id_does_not_exist(self):
        try:
            request = imgengine.TransformationRequest(self._image_format_mapper, 'nonexisting', (100, 100), domain.IMAGE_FORMAT_JPEG)
            self._image_server.prepare_transformation(request)
            self.fail()
        except imgengine.ImageMetadataNotFoundException, ex:
            self.assertEquals('nonexisting', ex.image_id)
    
    def test_preparing_transformation_should_update_file_system_and_database(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        request = imgengine.TransformationRequest(self._image_format_mapper, 'sampleId', (100, 100), domain.IMAGE_FORMAT_JPEG)
        result = self._image_server.prepare_transformation(request)
        
        derived_image_metadata = self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('sampleId', (100, 100), domain.IMAGE_FORMAT_JPEG)
        assert derived_image_metadata is not None
        self.assertEquals('sampleId-100x100-JPEG', derived_image_metadata.id)
        self.assertEquals(domain.IMAGE_FORMAT_JPEG, derived_image_metadata.format)
        self.assertEquals((100, 100), derived_image_metadata.size)
        self.assertEquals(domain.STATUS_OK, derived_image_metadata.status)
        self.assertEquals('sampleId', derived_image_metadata.original_image_metadata.id)
        
        self._derived_image_should_exist(derived_image_metadata)
    
    def test_prepare_transformation_should_always_return_the_same_path(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        request = imgengine.TransformationRequest(self._image_format_mapper, 'sampleId', (100, 100), domain.IMAGE_FORMAT_JPEG)
        result = self._image_server.prepare_transformation(request)
        result2 = self._image_server.prepare_transformation(request)
        self.assertEquals(result, result2)
    
    def test_cleanup_should_delete_inconsistent_original_and_derived_image_metadatas(self):    
        # create 10 original items and 4 derived items per original items 
        for i in range(1, 11):
            self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'item%s' % i)
         
            for size in [(100, 100), (200, 200), (300, 300), (400, 400)]:
                request = imgengine.TransformationRequest(self._image_format_mapper, 'item%s' % i, size, domain.IMAGE_FORMAT_JPEG)
                self._image_server.prepare_transformation(request)
        
        # now mark 5 of the original items as inconsistent, as well as their associated derived items
        def mark_original_image_metadatas_as_inconsistent(itemNumber):
            item = self._image_metadata_repository.find_original_image_metadata_by_id('item%s' % itemNumber)
            for di in item.derived_image_metadatas:
                di.status = domain.STATUS_INCONSISTENT
            item.status = domain.STATUS_INCONSISTENT
        
        for i in range(1, 6):
            def callback(session):
                mark_original_image_metadatas_as_inconsistent(i)
            self._template.do_with_session(callback)
            
        # finally, mark a few additional derived items as inconsistent, with their original item staying OK
        to_crush = [ self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (100, 100), domain.IMAGE_FORMAT_JPEG),
                    self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (200, 200), domain.IMAGE_FORMAT_JPEG),
                    self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (300, 300), domain.IMAGE_FORMAT_JPEG),
                    self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (400, 400), domain.IMAGE_FORMAT_JPEG) ]
        for item in to_crush:
            item.status = domain.STATUS_INCONSISTENT
        
        self._image_server.cleanup_inconsistent_items()

        for i in range(1, 6):
            self._original_image_should_not_exist(self._image_metadata_repository.find_original_image_metadata_by_id('item%s' % i))
        
        for i in range(6, 11):
            self._original_image_should_exist(self._image_metadata_repository.find_original_image_metadata_by_id('item%s' % i))
        
        self._derived_image_should_not_exist(self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (100, 100), domain.IMAGE_FORMAT_JPEG))
        self._derived_image_should_not_exist(self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (200, 200), domain.IMAGE_FORMAT_JPEG))       
        self._derived_image_should_exist(self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item7', (200, 200), domain.IMAGE_FORMAT_JPEG))         
   
    def _original_image_should_not_exist(self, original_image_metadata):
        assert original_image_metadata is None
        #self.assertFalse(os.path.exists(self._path_generator.original_path(original_image_metadata).absolute())) 
        
    def _original_image_should_exist(self, original_image_metadata):
        assert original_image_metadata is not None
        self.assertTrue(os.path.exists(self._path_generator.original_path(original_image_metadata).absolute())) 
        
    def _derived_image_should_not_exist(self, derived_image_metadata):
        assert derived_image_metadata is None
        #self.assertFalse(os.path.exists(self._path_generator.derived_path(derived_image_metadata).absolute())) 
    
    def _derived_image_should_exist(self, derived_image_metadata):
        assert derived_image_metadata is not None
        self.assertTrue(os.path.exists(self._path_generator.derived_path(derived_image_metadata).absolute())) 
    
    
    def test_should_return_original_image_path(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        path = self._image_server.get_original_image_path('sampleId')
        self.assertTrue(os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, path)))
    
    def test_should_not_return_original_image_path_when_item_does_not_exist(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        try:
            self._image_server.get_original_image_path('anyItem')
            self.fail()
        except imgengine.ImageMetadataNotFoundException, ex:
            self.assertEquals('anyItem', ex.image_id)
        
    def _sample_file_should_be_saved_correctly(self):
        assert os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')) == True
        self.assertEquals(os.path.getsize(JPG_SAMPLE_IMAGE_FILENAME), os.path.getsize(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')))        
    
    def test_deleting_image_should_delete_original_image_and_all_derived_images(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        self._image_server.prepare_transformation(imgengine.TransformationRequest(self._image_format_mapper, 'sampleId', (100, 100), domain.IMAGE_FORMAT_JPEG))
        self._image_server.prepare_transformation(imgengine.TransformationRequest(self._image_format_mapper, 'sampleId', (200, 200), domain.IMAGE_FORMAT_JPEG))
        self._image_server.delete('sampleId')
        
        self._sample_original_image_should_not_be_present()
        self._sample_100x100_image_should_not_be_present()
        self._sample_200x200_image_should_not_be_present()
    
    def _sample_original_image_should_not_be_present(self):
        assert self._image_metadata_repository.find_original_image_metadata_by_id('sampleId') is None
            
    def _sample_100x100_image_should_not_be_present(self):
        assert self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('sampleId', (100, 100), domain.IMAGE_FORMAT_JPEG) is None
    
    def _sample_200x200_image_should_not_be_present(self):
        assert self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('sampleId', (200, 200), domain.IMAGE_FORMAT_JPEG) is None
                  
