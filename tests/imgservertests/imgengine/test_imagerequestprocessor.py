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
import unittest
import os
import time
import random
import exceptions
from threading import Thread
from pkg_resources import resource_filename
from imgserver import imgengine, domain
from imgserver.imgengine.imagerequestprocessor import ItemDoesNotExistError
from imgserver.imgengine.transformationrequest import TransformationRequest
from tests.imgservertests.abstractintegrationtestcase import AbstractIntegrationTestCase

#JPG_SAMPLE_IMAGE_FILENAME = os.path.join('..', '..', 'samples', 'sami.jpg')
#BROKEN_IMAGE_FILENAME = os.path.join('..', '..', 'samples', 'brokenImage.jpg')
JPG_SAMPLE_IMAGE_FILENAME = resource_filename('imgserver.samples', 'sami.jpg')
BROKEN_IMAGE_FILENAME = resource_filename('imgserver.samples', 'brokenImage.jpg')
JPG_SAMPLE_IMAGE_SIZE = (3264, 2448)

class ImageRequestProcessorTestCase(AbstractIntegrationTestCase):
    
    def onSetUp(self):
        self._image_metadata_repository = self._imageServerFactory.image_metadata_repository
        self._schema_migrator = self._imageServerFactory.schema_migrator
        self._template = self._schema_migrator.session_template()
    
    def test_image_id_should_only_contain_alphanumeric_characters(self):
        try:
            self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId-')
        except imgengine.IDNotAuthorized, ex:
            assert ex.image_id == 'sampleId-'
    
    def test_should_not_save_broken_image(self):
        try:
            self._image_server.save_file_to_repository(BROKEN_IMAGE_FILENAME, 'sampleId')
        except imgengine.ImageFileNotRecognized, ex:
            pass
    
    def test_should_not_save_image_with_existing_id(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        try:
            self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')    
        except imgengine.ImageIDAlreadyExistingException, ex:
            assert ex.image_id == 'sampleId'
    
    def test_saving_image_should_update_file_system_and_database(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        self._sample_file_should_be_saved_correctly()
        
        item = self._image_metadata_repository.find_original_image_metadata_by_id('sampleId')
        assert item is not None
        assert item.id == 'sampleId'
        assert item.format == domain.IMAGE_FORMAT_JPEG
        assert item.size == JPG_SAMPLE_IMAGE_SIZE
        assert item.status == domain.STATUS_OK
    
    
    def test_save_image_should_accept_file_like_object_as_image_source(self):
        with open(JPG_SAMPLE_IMAGE_FILENAME, 'rb') as fobj:
            self._image_server.save_file_to_repository(fobj, 'sampleId')
            
        self._sample_file_should_be_saved_correctly()
    
    def test_should_not_prepare_transformation_when_id_does_not_exist(self):
        try:
            request = TransformationRequest('nonexisting', (100,100), domain.IMAGE_FORMAT_JPEG)
        except ItemDoesNotExistError, ex:
            self.assertEquals('nonexisting', ex.item_id)
    
    def test_preparing_transformation_should_update_file_system_and_database(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        request = TransformationRequest('sampleId', (100,100), domain.IMAGE_FORMAT_JPEG)
        result = self._image_server.prepare_transformation(request)
        assert os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'sampleId-100x100.jpg')) == True
        
        item = self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('sampleId', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert item is not None
        assert item.id == 'sampleId-100x100-JPEG'
        assert item.format == domain.IMAGE_FORMAT_JPEG
        assert item.size == (100,100)
        assert item.status == domain.STATUS_OK
        assert item.original_image_metadata.id == 'sampleId'
        
        # result should be consistent across calls (caching..)
        result2 = self._image_server.prepare_transformation(request)
        assert result == os.path.join('cache', 'sampleId-100x100.jpg')
        assert result2 == os.path.join('cache', 'sampleId-100x100.jpg')
    
    def test_cleanup_should_delete_inconsistent_original_and_derived_image_metadatas(self):
        
        # create 10 original items and 4 derived items per original items 
        for i in range(1,11):
            self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'item%s' %i)
         
            for size in [(100,100), (200,200), (300,300), (400,400)]:
                request = TransformationRequest('item%s' % i, size, domain.IMAGE_FORMAT_JPEG)
                self._image_server.prepare_transformation(request)
        
        # now mark 5 of the original items as inconsistent, as well as their associated derived items
        def mark_original_image_metadatas_as_inconsistent(itemNumber):
            item = self._image_metadata_repository.find_original_image_metadata_by_id('item%s' % itemNumber)
            for di in item.derivedItems:
                di.status = domain.STATUS_INCONSISTENT
                self._image_metadata_repository.update(di)
            item.status = domain.STATUS_INCONSISTENT
            self._image_metadata_repository.update(item)
        
        for i in range(1,6):
            def callback(session):
                mark_original_image_metadatas_as_inconsistent(i)
            self._template.do_with_session(callback)
            
        # finally, mark a few additional derived items as inconsistent, with their original item staying OK
        to_crush = [ self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (100,100),domain.IMAGE_FORMAT_JPEG),
                    self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (200,200),domain.IMAGE_FORMAT_JPEG),
                    self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (300,300),domain.IMAGE_FORMAT_JPEG),
                    self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (400,400),domain.IMAGE_FORMAT_JPEG) ]
        for item in to_crush:
            item.status = domain.STATUS_INCONSISTENT
            self._image_metadata_repository.update(item)
        
        self._image_server.cleanup_inconsistent_items()
        
        # items 1 to 5 should not exist anymore (DB and file)
        for i in range(1,6):
            item = self._image_metadata_repository.find_original_image_metadata_by_id('item%s' % i)
            assert item is None
            assert os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'item%s.jpg' %(i))) == False
        
        # items 6 to 10 should still be OK
        for i in range(6,11):
            item = self._image_metadata_repository.find_original_image_metadata_by_id('item%s' % i)
            assert item is not None
            assert os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'item%s.jpg' %(i))) 
        
        # a few Derived Items that should be KO
        assert self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (100,100),domain.IMAGE_FORMAT_JPEG) is None
        assert os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'item6-100x100.jpg')) == False
        assert self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item6', (200,200),domain.IMAGE_FORMAT_JPEG) is None
        assert os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'item6-200x200.jpg')) == False
        
        # a few Derived Items that should be OK
        assert self._image_metadata_repository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('item7', (200,200),domain.IMAGE_FORMAT_JPEG) is not None
        assert os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'item7-200x200.jpg')) == True
    
    def test_should_return_original_image_path(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        path = self._image_server.get_original_image_path('sampleId')
        self.assertTrue(os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, path)))
    
    def test_should_not_return_original_image_path_when_item_does_not_exist(self):
        self._image_server.save_file_to_repository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        try:
            self._image_server.get_original_image_path('anyItem')
            self.fail()
        except ItemDoesNotExistError, ex:
            self.assertEquals('anyItem', ex.item_id)
        
    def _sample_file_should_be_saved_correctly(self):
        assert os.path.exists(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')) == True
        self.assertEquals(os.path.getsize(JPG_SAMPLE_IMAGE_FILENAME), os.path.getsize(os.path.join(AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')))        
