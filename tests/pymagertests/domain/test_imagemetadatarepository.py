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

import unittest
from pymager import domain

from tests.pymagertests.abstractintegrationtestcase import AbstractIntegrationTestCase

class ImageMetadataRepositoryTestCase(AbstractIntegrationTestCase):
    
    def onSetUp(self):
        self._itemRepository = self._image_server_factory.image_metadata_repository 
        self._schema_migrator = self._image_server_factory.schema_migrator
        self._template = self._image_server_factory.session_template
        
    def test_should_not_find_original_image_metadata_because_of_unknown_id(self):
        assert self._itemRepository.find_original_image_metadata_by_id('anyId') is None
    
    def test_should_find_original_image_metadata_by_id(self):
        item = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(item)
        found_item = self._itemRepository.find_original_image_metadata_by_id('MYID12435')
        assert found_item is not None
        assert found_item.id == 'MYID12435'
        assert found_item.status == domain.STATUS_OK
        assert found_item.width == 800
        assert found_item.height == 600
        assert found_item.format == domain.IMAGE_FORMAT_JPEG
        _datetimes_should_be_equal(item.last_status_change_date, found_item.last_status_change_date)
    
    def test_should_update_original_image_metadata(self):
        item = domain.OriginalImageMetadata('MYID12435', domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(item)
        item.status = domain.STATUS_OK
        #self._itemRepository.update(item)
        found_item = self._itemRepository.find_original_image_metadata_by_id('MYID12435')
        assert found_item is not None
        assert found_item.id == 'MYID12435'
        assert found_item.status == domain.STATUS_OK
        assert found_item.width == 800
        assert found_item.height == 600
        assert found_item.format == domain.IMAGE_FORMAT_JPEG
        _datetimes_should_be_equal(item.last_status_change_date, found_item.last_status_change_date)

    
    def test_should_update_derived_image_metadata(self):
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
        
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)
        found_item = self._itemRepository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('MYID12435', (100, 100), domain.IMAGE_FORMAT_JPEG)
        assert found_item is not None
        assert found_item.status == domain.STATUS_OK
        assert found_item.width == 100
        assert found_item.height == 100
        assert found_item.format == domain.IMAGE_FORMAT_JPEG
        assert found_item.original_image_metadata.id == 'MYID12435'
        assert found_item.original_image_metadata.status == domain.STATUS_OK
        assert found_item.original_image_metadata.width == 800
        assert found_item.original_image_metadata.height == 600
        assert found_item.original_image_metadata.format == domain.IMAGE_FORMAT_JPEG
        _datetimes_should_be_equal(item.last_status_change_date, found_item.last_status_change_date)
    
    def test_should_find_derived_image_metadata_by_original_image_metadata_id_size_and_format(self):
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
        
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)
        found_item = self._itemRepository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('MYID12435', (100, 100), domain.IMAGE_FORMAT_JPEG)    
        
        assert found_item is not None
        assert found_item.status == domain.STATUS_OK
        assert found_item.width == 100
        assert found_item.height == 100
        assert found_item.format == domain.IMAGE_FORMAT_JPEG
        assert found_item.original_image_metadata.id == 'MYID12435'
        assert found_item.original_image_metadata.status == domain.STATUS_OK
        assert found_item.original_image_metadata.width == 800
        assert found_item.original_image_metadata.height == 600
        assert found_item.original_image_metadata.format == domain.IMAGE_FORMAT_JPEG
        _datetimes_should_be_equal(item.last_status_change_date, found_item.last_status_change_date)
    
    def test_should_delete_original_image_metadata(self):
        item = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(item)
        self._itemRepository.delete(self._itemRepository.find_original_image_metadata_by_id('MYID12435'))
        
        found_item = self._itemRepository.find_original_image_metadata_by_id('MYID12435')
        assert found_item is None
        
    def test_deletion_of_derived_image_metadata_should_not_delete_associated_derived_image_metadatas(self):
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
    
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)
    
        self._session.delete(self._itemRepository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('MYID12435', (100, 100), domain.IMAGE_FORMAT_JPEG))
        
        found_item = self._itemRepository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('MYID12435', (100, 100), domain.IMAGE_FORMAT_JPEG)
        assert found_item is None
        
        found_original_image_metadata = self._itemRepository.find_original_image_metadata_by_id('MYID12435')
        assert found_original_image_metadata is not None
    
    def test_deletion_of_original_image_metadata_should_delete_associated_derived_image_metadatas(self):        
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
    
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)

        self._session.delete(self._itemRepository.find_original_image_metadata_by_id('MYID12435'))
            
        found_derived_image_metadata = self._itemRepository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('MYID12435', (100, 100), domain.IMAGE_FORMAT_JPEG)
        assert found_derived_image_metadata is None
        
        found_original_image_metadata = self._itemRepository.find_original_image_metadata_by_id('MYID12435')
        assert found_original_image_metadata is None
        
    def test_should_navigate_to_derived_image_metadatas_from_original_image_metadata(self):
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
        
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)
        
        found_item = self._itemRepository.find_original_image_metadata_by_id('MYID12435')    
        assert found_item is not None
        assert found_item.derived_image_metadatas is not None
        assert len(found_item.derived_image_metadatas) == 1
        assert found_item.derived_image_metadatas[0].id == item.id
    
    def test_should_not_find_derived_image_metadata_because_of_width(self):
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
        
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)
        found_item = self._itemRepository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('MYID12435', (101, 100), domain.IMAGE_FORMAT_JPEG)
        assert found_item is None
        
    def test_should_not_find_derived_image_metadata_because_of_height(self):
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
        
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)
        found_item = self._itemRepository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('MYID12435', (100, 101), domain.IMAGE_FORMAT_JPEG)
        assert found_item is None
    
    def test_should_not_find_derived_image_metadata_because_of_id(self):
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
        
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)
        found_item = self._itemRepository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('ANOTHERID', (100, 100), domain.IMAGE_FORMAT_JPEG)
        assert found_item is None
        
    def test_should_not_find_derived_image_metadata_because_of_format(self):
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
        
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)
        found_item = self._itemRepository.find_derived_image_metadata_by_original_image_metadata_id_size_and_format('MYID12435', (100, 100), 'JPEG2')
        assert found_item is None
    
    def test_should_not_save_two_original_image_metadatas_with_same_id(self):
        item = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        item2 = domain.OriginalImageMetadata('MYID12435', domain.STATUS_INCONSISTENT, (700, 100), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(item)
        try:
            self._itemRepository.add(item2)
        except domain.DuplicateEntryException, ex:
            assert 'MYID12435' == ex.duplicate_id
        else:
            self.fail()
            
    def test_should_not_save_two_derived_image_metadatas_with_same_id(self):
        original_image_metadata = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.add(original_image_metadata)
        item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
        self._itemRepository.add(item)
        
        try:
            item2 = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
            self._itemRepository.add(item2)
        except domain.DuplicateEntryException as ex:
            assert 'MYID12435-100x100-JPEG' == ex.duplicate_id
        except Exception as e:
            print e
        else:
            self.fail()
            
    def test_should_find_inconsistent_original_image_metadatas(self):
        for i in range(1, 15):
            item = domain.OriginalImageMetadata('MYID%s' % i, domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.add(item)
        
        for i in range(16, 20):
            item = domain.OriginalImageMetadata('MYID%s' % i, domain.STATUS_OK, (900, 400), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.add(item)    
        
        items = self._itemRepository.find_inconsistent_original_image_metadatas(10)
        assert len(items) == 10
        for i in items:
            assert i.id in ['MYID%s' % n for n in range(1, 15) ]
            assert i.status == domain.STATUS_INCONSISTENT
            assert i.width == 800
            assert i.height == 600
            assert i.format == domain.IMAGE_FORMAT_JPEG
    
    def test_should_find_inconsistent_derived_image_metadatas(self):
        
        for i in range(1, 15):
            original_image_metadata = domain.OriginalImageMetadata('MYID%s' % i, domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.add(original_image_metadata)
        
            item = domain.DerivedImageMetadata(domain.STATUS_INCONSISTENT, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
            self._itemRepository.add(item)
        
        
        for i in range(16, 20):
            original_image_metadata = domain.OriginalImageMetadata('MYID%s' % i, domain.STATUS_OK, (900, 400), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.add(original_image_metadata)    
            
            item = domain.DerivedImageMetadata(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_image_metadata)
            self._itemRepository.add(item)
        
        items = self._itemRepository.find_inconsistent_derived_image_metadatas(10)
        assert len(items) == 10
        for i in items:
            assert i.id in ['MYID%s-100x100-JPEG' % n for n in range(1, 15) ]
            assert i.status == domain.STATUS_INCONSISTENT
            assert i.width == 100
            assert i.height == 100
            assert i.format == domain.IMAGE_FORMAT_JPEG

def _datetimes_should_be_equal(datetime1, datetime2):
    delta = datetime1 - datetime2
    assert delta.days == 0
    assert delta.seconds == 0
