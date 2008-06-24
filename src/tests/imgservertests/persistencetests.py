import unittest
from imgserver import domain, persistence
from tests import support
from imgserver.domain.abstractitem import AbstractItem
from imgserver.domain.originalitem import OriginalItem
from imgserver.domain.deriveditem import DerivedItem

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
        _dateTimesAreConsideredEqual(item.lastStatusChangeDate, foundItem.lastStatusChangeDate)
        
    def testShouldDeleteOriginalItem(self):
        item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        self._itemRepository.delete(item)
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
        _dateTimesAreConsideredEqual(item.lastStatusChangeDate, foundItem.lastStatusChangeDate)

    
    def testShouldUpdateDerivedItem(self):
        originalItem = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100),domain.IMAGE_FORMAT_JPEG)
        assert foundItem is not None
        assert foundItem.status == domain.STATUS_OK
        assert foundItem.width == 100
        assert foundItem.height == 100
        assert foundItem.format == domain.IMAGE_FORMAT_JPEG
        assert foundItem.originalItem.id == 'MYID12435'
        assert foundItem.originalItem.status == domain.STATUS_OK
        assert foundItem.originalItem.width == 800
        assert foundItem.originalItem.height == 600
        assert foundItem.originalItem.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.lastStatusChangeDate, foundItem.lastStatusChangeDate)
    
    def testShouldNotFindAnyOriginalItem(self):
        foundItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundItem is None
        
    def testShouldSaveAndFindDerivedItemByOriginalItemIdSizeAndFormat(self):
        originalItem = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert foundItem is not None
        assert foundItem.status == domain.STATUS_OK
        assert foundItem.width == 100
        assert foundItem.height == 100
        assert foundItem.format == domain.IMAGE_FORMAT_JPEG
        assert foundItem.originalItem.id == 'MYID12435'
        assert foundItem.originalItem.status == domain.STATUS_OK
        assert foundItem.originalItem.width == 800
        assert foundItem.originalItem.height == 600
        assert foundItem.originalItem.format == domain.IMAGE_FORMAT_JPEG
        _dateTimesAreConsideredEqual(item.lastStatusChangeDate, foundItem.lastStatusChangeDate)
        
    def testDeleteDerivedItemShouldNotDeleteAssociatedOriginalItem(self):
        originalItem = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        
        def callback(session):
            session.delete(self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG))
            
        self._template.do_with_session(callback)
        
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
        
        foundOriginalItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundOriginalItem is not None
        
    def testShouldFindDerivedItemsFromOriginalItem(self):
        originalItem = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        
        def callback(session):
            foundItem = self._itemRepository.findOriginalItemById('MYID12435')    
            assert foundItem is not None
            assert foundItem.derivedItems is not None
            assert len(foundItem.derivedItems) == 1
            assert foundItem.derivedItems[0].id == item.id
        
        self._template.do_with_session(callback)
    
    def testShouldNotFindAnyDerivedItemIfWidthDoesNotMatch(self):
        originalItem = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (101,100), domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
        
    def testShouldNotFindAnyDerivedItemIfHeightDoesNotMatch(self):
        originalItem = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,101), domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
    
    def testShouldNotFindAnyDerivedItemIfIdDoesNotMatch(self):
        originalItem = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('ANOTHERID', (100,100),domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
        
    def testShouldNotFindAnyDerivedItemIfFormatNotMatch(self):
        originalItem = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100),'JPEG2')
        assert foundItem is None
    
    def testSaveTwoOriginalItemsWithSameIDShouldThrowException(self):
        item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        item2 = OriginalItem('MYID12435', domain.STATUS_INCONSISTENT, (700, 100), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        try:
            self._itemRepository.create(item2)
        except persistence.DuplicateEntryException, ex:
            assert 'MYID12435' == ex.duplicateId
        else:
            self.fail()
            
    def testSaveTwoDerivedItemsWithSameIDShouldThrowException(self):
        originalItem = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
            
        try:
            item2 = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
            self._itemRepository.create(item2)
        except persistence.DuplicateEntryException, ex:
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
            originalItem = OriginalItem('MYID%s' %i, domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(originalItem)
        
            item = DerivedItem(domain.STATUS_INCONSISTENT, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
            self._itemRepository.create(item)
        
        
        for i in range(16,20):
            originalItem = OriginalItem('MYID%s' %i, domain.STATUS_OK, (900, 400), domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(originalItem)    
            
            item = DerivedItem(domain.STATUS_OK, (100, 100), domain.IMAGE_FORMAT_JPEG, originalItem)
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

