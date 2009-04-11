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
import unittest
from imgserver import domain
from tests import support
from imgserver.domain.abstractitem import AbstractItem
from imgserver.domain.originalitem import OriginalItem
from imgserver.domain.deriveditem import DerivedItem
from imgserver.domain.itemrepository import DuplicateEntryException

def _dateTimesAreConsideredEqual(datetime1, datetime2):
    delta = datetime1 - datetime2
    assert delta.days == 0
    assert delta.seconds == 0

class ItemRepositoryTestCase(support.AbstractIntegrationTestCase):
    
    def onSetUp(self):
        self._itemRepository = self._imageServerFactory.item_repository 
        self._schema_migrator = self._imageServerFactory.schema_migrator
        self._template = self._schema_migrator.session_template()
    
    def testShouldNotFindAnyItemWhenIdDoesNotExist(self):
        assert self._itemRepository.find_original_item_by_id('anyId') is None
    
    def testShouldSaveAndFindOriginalItem(self):
        item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        found_item = self._itemRepository.find_original_item_by_id('MYID12435')
        assert found_item is not None
        assert found_item.id == 'MYID12435'
        assert found_item.status == domain.STATUS_OK
        assert found_item.width == 800
        assert found_item.height == 600
        assert found_item.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.last_status_change_date, found_item.last_status_change_date)
    
    def testShouldUpdateOriginalItem(self):
        item = OriginalItem('MYID12435', domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        item.status = domain.STATUS_OK
        self._itemRepository.update(item)
        found_item = self._itemRepository.find_original_item_by_id('MYID12435')
        assert found_item is not None
        assert found_item.id == 'MYID12435'
        assert found_item.status == domain.STATUS_OK
        assert found_item.width == 800
        assert found_item.height == 600
        assert found_item.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.last_status_change_date, found_item.last_status_change_date)

    
    def testShouldUpdateDerivedItem(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        found_item = self._itemRepository.find_derived_item_by_original_item_id_size_and_format('MYID12435', (100,100),domain.IMAGE_FORMAT_JPEG)
        assert found_item is not None
        assert found_item.status == domain.STATUS_OK
        assert found_item.width == 100
        assert found_item.height == 100
        assert found_item.format == domain.IMAGE_FORMAT_JPEG
        assert found_item.original_item.id == 'MYID12435'
        assert found_item.original_item.status == domain.STATUS_OK
        assert found_item.original_item.width == 800
        assert found_item.original_item.height == 600
        assert found_item.original_item.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.last_status_change_date, found_item.last_status_change_date)
    
    def testShouldNotFindAnyOriginalItem(self):
        found_item = self._itemRepository.find_original_item_by_id('MYID12435')
        assert found_item is None
        
    def testShouldSaveAndFindDerivedItemByOriginalItemIdSizeAndFormat(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        found_item = self._itemRepository.find_derived_item_by_original_item_id_size_and_format('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert found_item is not None
        assert found_item.status == domain.STATUS_OK
        assert found_item.width == 100
        assert found_item.height == 100
        assert found_item.format == domain.IMAGE_FORMAT_JPEG
        assert found_item.original_item.id == 'MYID12435'
        assert found_item.original_item.status == domain.STATUS_OK
        assert found_item.original_item.width == 800
        assert found_item.original_item.height == 600
        assert found_item.original_item.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.last_status_change_date, found_item.last_status_change_date)
    
    def testShouldDeleteOriginalItem(self):
        def callback(session):
            item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(item)
            self._itemRepository.delete(self._itemRepository.find_original_item_by_id('MYID12435'))
        self._template.do_with_session(callback)    
        
        found_item = self._itemRepository.find_original_item_by_id('MYID12435')
        assert found_item is None
        
    def testDeleteDerivedItemShouldNotDeleteAssociatedOriginalItem(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        
        def callback(session):
            session.delete(self._itemRepository.find_derived_item_by_original_item_id_size_and_format('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG))
            
        self._template.do_with_session(callback)
        
        found_item = self._itemRepository.find_derived_item_by_original_item_id_size_and_format('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert found_item is None
        
        foundOriginalItem = self._itemRepository.find_original_item_by_id('MYID12435')
        assert foundOriginalItem is not None
    
    def testDeleteOriginalItemShouldDeleteAssociatedDerivedItems(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        
        def callback(session):
            session.delete(self._itemRepository.find_original_item_by_id('MYID12435'))
            
        self._template.do_with_session(callback)
        
        found_derived_item = self._itemRepository.find_derived_item_by_original_item_id_size_and_format('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert found_derived_item is None
        
        found_original_item = self._itemRepository.find_original_item_by_id('MYID12435')
        assert found_original_item is None
        
    def testShouldFindDerivedItemsFromOriginalItem(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        
        def callback(session):
            found_item = self._itemRepository.find_original_item_by_id('MYID12435')    
            assert found_item is not None
            assert found_item.derivedItems is not None
            assert len(found_item.derivedItems) == 1
            assert found_item.derivedItems[0].id == item.id
        
        self._template.do_with_session(callback)
    
    def testShouldNotFindAnyDerivedItemIfWidthDoesNotMatch(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        found_item = self._itemRepository.find_derived_item_by_original_item_id_size_and_format('MYID12435', (101,100), domain.IMAGE_FORMAT_JPEG)
        assert found_item is None
        
    def testShouldNotFindAnyDerivedItemIfHeightDoesNotMatch(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        found_item = self._itemRepository.find_derived_item_by_original_item_id_size_and_format('MYID12435', (100,101), domain.IMAGE_FORMAT_JPEG)
        assert found_item is None
    
    def testShouldNotFindAnyDerivedItemIfIdDoesNotMatch(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        found_item = self._itemRepository.find_derived_item_by_original_item_id_size_and_format('ANOTHERID', (100,100),domain.IMAGE_FORMAT_JPEG)
        assert found_item is None
        
    def testShouldNotFindAnyDerivedItemIfFormatNotMatch(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        found_item = self._itemRepository.find_derived_item_by_original_item_id_size_and_format('MYID12435', (100,100),'JPEG2')
        assert found_item is None
    
    def testSaveTwoOriginalItemsWithSameIDShouldThrowException(self):
        item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        item2 = OriginalItem('MYID12435', domain.STATUS_INCONSISTENT, (700, 100), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        try:
            self._itemRepository.create(item2)
        except DuplicateEntryException, ex:
            assert 'MYID12435' == ex.duplicate_id
        else:
            self.fail()
            
    def testSaveTwoDerivedItemsWithSameIDShouldThrowException(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
            
        try:
            item2 = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
            self._itemRepository.create(item2)
        except DuplicateEntryException, ex:
            assert 'MYID12435-100x100-JPEG' == ex.duplicate_id
        else:
            self.fail()
            
    def testShouldFindInconsistentOriginalItems(self):
        for i in range(1,15):
            item = OriginalItem('MYID%s' %i, domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(item)
        
        for i in range(16,20):
            item = OriginalItem('MYID%s' %i, domain.STATUS_OK, (900, 400), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(item)    
        
        items =  self._itemRepository.find_inconsistent_original_items(10)
        assert len(items) == 10
        for i in items:
            assert i.id in ['MYID%s' %n for n in range(1,15) ]
            assert i.status == domain.STATUS_INCONSISTENT
            assert i.width == 800
            assert i.height == 600
            assert i.format == domain.IMAGE_FORMAT_JPEG
    
    def testShouldFindInconsistentDerivedItems(self):
        
        for i in range(1,15):
            original_item = OriginalItem('MYID%s' %i, domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(original_item)
        
            item = DerivedItem(domain.STATUS_INCONSISTENT, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
            self._itemRepository.create(item)
        
        
        for i in range(16,20):
            original_item = OriginalItem('MYID%s' %i, domain.STATUS_OK, (900, 400), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(original_item)    
            
            item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
            self._itemRepository.create(item)
        
        items =  self._itemRepository.find_inconsistent_derived_items(10)
        assert len(items) == 10
        for i in items:
            assert i.id in ['MYID%s-100x100-JPEG' %n for n in range(1,15) ]
            assert i.status == domain.STATUS_INCONSISTENT
            assert i.width == 100
            assert i.height == 100
            assert i.format == domain.IMAGE_FORMAT_JPEG

def suite():
    return unittest.makeSuite(PersistenceTestCase, 'test')

