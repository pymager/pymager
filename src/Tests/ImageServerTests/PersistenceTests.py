import unittest
from ImageServer import Domain
from Tests import Support

class PersistenceTestCase(Support.AbstractIntegrationTestCase):
    
    def onSetUp(self):
        self.itemRepository = self.imageServerFactory.getItemRepository() 
    
    def testShouldNotFindAnyItemWhenIdDoesNotExist(self):
        assert self.itemRepository.findOriginalItemById('anyId') is None
    
    def testShouldSaveOriginalItem(self):
        item = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), 'JPEG')
        self.itemRepository.create(item)
        foundItem = self.itemRepository.findOriginalItemById('MYID12435')
        assert foundItem is not None
        assert foundItem.id == 'MYID12435'
        assert foundItem.status == Domain.STATUS_OK
        assert foundItem.width == 800
        assert foundItem.height == 600
        assert foundItem.format == 'JPEG'

        
    def testFindDerivedItemByOriginalItemIdAndSizeShouldFindSavedDerivedItem(self):
        originalItem = Domain.OriginalItem('MYID12435', Domain.STATUS_OK, (800, 600), 'JPEG')
        self.itemRepository.create(originalItem)
        
        item = Domain.DerivedItem(Domain.STATUS_OK, (100, 100), 'JPEG', originalItem)
        self.itemRepository.create(item)
        foundItem = self.itemRepository.findDerivedItemByOriginalItemIdAndSize('MYID12435', (100,100))
        assert foundItem is not None
        assert foundItem.status == Domain.STATUS_OK
        assert foundItem.width == 100
        assert foundItem.height == 100
        assert foundItem.format == 'JPEG'
        assert foundItem.originalItem.id == 'MYID12435'
        assert foundItem.originalItem.status == Domain.STATUS_OK
        assert foundItem.originalItem.width == 800
        assert foundItem.originalItem.height == 600
        assert foundItem.originalItem.format == 'JPEG'

def suite():
    return unittest.makeSuite(PersistenceTestCase, 'test')

