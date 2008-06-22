import unittest
from ImageServer import Domain, Persistence
from Tests import Support

class PersistenceTestCase(Support.AbstractIntegrationTestCase):
    
    def onSetUp(self):
        self._itemRepository = self._imageServerFactory.getItemRepository() 
        self._persistenceProvider = self._imageServerFactory.getPersistenceProvider()
    
    def testShouldNotFindAnyItemWhenIdDoesNotExist(self):
        assert self._itemRepository.findOriginalItemById('anyId') is None
    
    def testShouldSaveAndFindOriginalItem(self):
        item = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundItem is not None
        assert foundItem.id == 'MYID12435'
        assert foundItem.status == Domain.STATUS_OK
        assert foundItem.width == 800
        assert foundItem.height == 600
        assert foundItem.format == Domain.IMAGE_FORMAT_JPEG
    
    def testShouldUpdateOriginalItem(self):
        item = Domain.OriginalItem('MYID12435', Domain.STATUS_INCONSISTENT, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        item.status = Domain.STATUS_OK
        self._itemRepository.update(item)
        foundItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundItem is not None
        assert foundItem.id == 'MYID12435'
        assert foundItem.status == Domain.STATUS_OK
        assert foundItem.width == 800
        assert foundItem.height == 600
        assert foundItem.format == Domain.IMAGE_FORMAT_JPEG

    
    def testShouldUpdateDerivedItem(self):
        originalItem = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), Domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100),Domain.IMAGE_FORMAT_JPEG)
        assert foundItem is not None
        assert foundItem.status == Domain.STATUS_OK
        assert foundItem.width == 100
        assert foundItem.height == 100
        assert foundItem.format == Domain.IMAGE_FORMAT_JPEG
        assert foundItem.originalItem.id == 'MYID12435'
        assert foundItem.originalItem.status == Domain.STATUS_OK
        assert foundItem.originalItem.width == 800
        assert foundItem.originalItem.height == 600
        assert foundItem.originalItem.format == Domain.IMAGE_FORMAT_JPEG
    
    def testShouldNotFindAnyOriginalItem(self):
        foundItem = self._itemRepository.findOriginalItemById('MYID12435')
        assert foundItem is None
        
    def testShouldSaveAndFindDerivedItemByOriginalItemIdSizeAndFormat(self):
        originalItem = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), Domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100), Domain.IMAGE_FORMAT_JPEG)
        assert foundItem is not None
        assert foundItem.status == Domain.STATUS_OK
        assert foundItem.width == 100
        assert foundItem.height == 100
        assert foundItem.format == Domain.IMAGE_FORMAT_JPEG
        assert foundItem.originalItem.id == 'MYID12435'
        assert foundItem.originalItem.status == Domain.STATUS_OK
        assert foundItem.originalItem.width == 800
        assert foundItem.originalItem.height == 600
        assert foundItem.originalItem.format == Domain.IMAGE_FORMAT_JPEG
        
    def testShouldFindDerivedItemsFromOriginalItem(self):
        originalItem = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), Domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        
        def callback(session, foundItem):    
            assert foundItem is not None
            assert foundItem.derivedItems is not None
            assert len(foundItem.derivedItems) == 1
            assert foundItem.derivedItems[0].id == item.id
        
        self._itemRepository.findOriginalItemById('MYID12435', callback)
    
    def testShouldNotFindAnyDerivedItemIfWidthDoesNotMatch(self):
        originalItem = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), Domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (101,100), Domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
        
    def testShouldNotFindAnyDerivedItemIfHeightDoesNotMatch(self):
        originalItem = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), Domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,101), Domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
    
    def testShouldNotFindAnyDerivedItemIfIdDoesNotMatch(self):
        originalItem = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), Domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('ANOTHERID', (100,100),Domain.IMAGE_FORMAT_JPEG)
        assert foundItem is None
        
    def testShouldNotFindAnyDerivedItemIfFormatNotMatch(self):
        originalItem = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        
        item = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), Domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
        foundItem = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('MYID12435', (100,100),'JPEG2')
        assert foundItem is None
    
    def testSaveTwoOriginalItemsWithSameIDShouldThrowException(self):
        item = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        item2 = Domain.OriginalItem('MYID12435', Domain.STATUS_INCONSISTENT, (700, 100), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(item)
        try:
            self._itemRepository.create(item2)
        except Persistence.DuplicateEntryException, ex:
            assert 'MYID12435' == ex.duplicateId
        else:
            self.fail()
            
    def testSaveTwoDerivedItemsWithSameIDShouldThrowException(self):
        originalItem = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), Domain.IMAGE_FORMAT_JPEG)
        self._itemRepository.create(originalItem)
        item = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), Domain.IMAGE_FORMAT_JPEG, originalItem)
        self._itemRepository.create(item)
            
        try:
            item2 = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), Domain.IMAGE_FORMAT_JPEG, originalItem)
            self._itemRepository.create(item2)
        except Persistence.DuplicateEntryException, ex:
            assert 'MYID12435-100x100-JPEG' == ex.duplicateId
        else:
            self.fail()
            
    def testShouldFindInconsistentItems(self):
        for i in range(1,15):
            item = Domain.OriginalItem('MYID%s' %i, Domain.STATUS_INCONSISTENT, (800, 600), Domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(item)
        
        for i in range(16,20):
            item = Domain.OriginalItem('MYID%s' %i, Domain.STATUS_OK, (900, 400), Domain.IMAGE_FORMAT_JPEG)
            self._itemRepository.create(item)    
        
        items =  self._itemRepository.findInconsistentOriginalItems(10)
        assert len(items) == 10
        for i in items:
            assert i.id in ['MYID%s' %n for n in range(1,15) ]
            assert i.status == Domain.STATUS_INCONSISTENT
            assert i.width == 800
            assert i.height == 600
            assert i.format == Domain.IMAGE_FORMAT_JPEG

def suite():
    return unittest.makeSuite(PersistenceTestCase, 'test')

