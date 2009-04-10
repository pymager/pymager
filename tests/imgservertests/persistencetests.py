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
from imgserver import domain, persistence
from tests import support
from imgserver.domain.abstractitem import AbstractItem
from imgserver.domain.originalitem import OriginalItem
from imgserver.domain.deriveditem import DerivedItem
from imgserver.domain.itemrepository import DuplicateEntryException

def _dateTimesAreConsideredEqual(datetime1, datetime2):
    delta = datetime1 - datetime2
    assert delta.days == 0
    assert delta.seconds == 0

class PersistenceTestCase(support.AbstractIntegrationTestCase):
    
    def onSetUp(self):
        self._itemRepository = self._imageServerFactory.getItemRepository() 
        self._persistenceProvider = self._imageServerFactory.getPersistenceProvider()
        self._template = self._persistenceProvider.session_template()
    
    def testShouldNotFindAnyItemWhenIdDoesNotExist(self):
        assert self._itemRepository.findOriginalItemById('anyId') is None
    
    def testShouldSaveAndFindOriginalItem(self):
        item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundItem is not None
        assert foundItem.id == 'MYID12435'
        assert foundItem.status == domain.STATUS_OK
        assert foundItem.width == 800
        assert foundItem.height == 600
        assert foundItem.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.last_status_change_date, foundItem.last_status_change_date)
        
    def testShouldDeleteOriginalItem(self):
        def callback(session):
            item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(item)
            self._itemRepository.delete(self._itemRepository.findOriginalItemById('MYID12435'))
        self._template.do_with_session(callback)    
        
        foundItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundItem is None
    
    def testShouldUpdateOriginalItem(self):
        item = OriginalItem('MYID12435', domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        item.status = domain.STATUS_OK
        self._itemRepository.update(item)
        foundItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundItem is not None
        assert foundItem.id == 'MYID12435'
        assert foundItem.status == domain.STATUS_OK
        assert foundItem.width == 800
        assert foundItem.height == 600
        assert foundItem.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.last_status_change_date, foundItem.last_status_change_date)

    
    def testShouldUpdateDerivedItem(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100),domain.IMAGE_FORMAT_JPEG)
        assert foundItem is not None
        assert foundItem.status == domain.STATUS_OK
        assert foundItem.width == 100
        assert foundItem.height == 100
        assert foundItem.format == domain.IMAGE_FORMAT_JPEG
        assert foundItem.original_item.id == 'MYID12435'
        assert foundItem.original_item.status == domain.STATUS_OK
        assert foundItem.original_item.width == 800
        assert foundItem.original_item.height == 600
        assert foundItem.original_item.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.last_status_change_date, foundItem.last_status_change_date)
    
    def testShouldNotFindAnyOriginalItem(self):
        foundItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundItem is None
        
    def testShouldSaveAndFindDerivedItemByOriginalItemIdSizeAndFormat(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert foundItem is not None
        assert foundItem.status == domain.STATUS_OK
        assert foundItem.width == 100
        assert foundItem.height == 100
        assert foundItem.format == domain.IMAGE_FORMAT_JPEG
        assert foundItem.original_item.id == 'MYID12435'
        assert foundItem.original_item.status == domain.STATUS_OK
        assert foundItem.original_item.width == 800
        assert foundItem.original_item.height == 600
        assert foundItem.original_item.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.last_status_change_date, foundItem.last_status_change_date)
        
    def testDeleteDerivedItemShouldNotDeleteAssociatedOriginalItem(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        
        def callback(session):
            session.delete(self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG))
            
        self._template.do_with_session(callback)
        
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
        
        foundOriginalItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundOriginalItem is not None
        
    def testShouldFindDerivedItemsFromOriginalItem(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        
        def callback(session):
            foundItem = self._itemRepository.findOriginalItemById('MYID12435')    
            assert foundItem is not None
            assert foundItem.derivedItems is not None
            assert len(foundItem.derivedItems) == 1
            assert foundItem.derivedItems[0].id == item.id
        
        self._template.do_with_session(callback)
    
    def testShouldNotFindAnyDerivedItemIfWidthDoesNotMatch(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (101,100), domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
        
    def testShouldNotFindAnyDerivedItemIfHeightDoesNotMatch(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,101), domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
    
    def testShouldNotFindAnyDerivedItemIfIdDoesNotMatch(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('ANOTHERID', (100,100),domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
        
    def testShouldNotFindAnyDerivedItemIfFormatNotMatch(self):
        original_item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(original_item)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, original_item)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100),'JPEG2')
        assert foundItem is None
    
    def testSaveTwoOriginalItemsWithSameIDShouldThrowException(self):
        item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        item2 = OriginalItem('MYID12435', domain.STATUS_INCONSISTENT, (700, 100), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        try:
            self._itemRepository.create(item2)
        except DuplicateEntryException, ex:
            assert 'MYID12435' == ex.duplicateId
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
            assert 'MYID12435-100x100-JPEG' == ex.duplicateId
        else:
            self.fail()
            
    def testShouldFindInconsistentOriginalItems(self):
        for i in range(1,15):
            item = OriginalItem('MYID%s' %i, domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(item)
        
        for i in range(16,20):
            item = OriginalItem('MYID%s' %i, domain.STATUS_OK, (900, 400), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(item)    
        
        items =  self._itemRepository.findInconsistentOriginalItems(10)
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
        
        items =  self._itemRepository.findInconsistentDerivedItems(10)
        assert len(items) == 10
        for i in items:
            assert i.id in ['MYID%s-100x100-JPEG' %n for n in range(1,15) ]
            assert i.status == domain.STATUS_INCONSISTENT
            assert i.width == 100
            assert i.height == 100
            assert i.format == domain.IMAGE_FORMAT_JPEG

def suite():
    return unittest.makeSuite(PersistenceTestCase, 'test')

