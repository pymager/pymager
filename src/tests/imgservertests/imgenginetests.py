import unittest
import os
import time
import random
from threading import Thread
from tests import support
from imgserver import imgengine, domain

NB_THREADS = 15

#JPG_SAMPLE_IMAGE_FILENAME = os.path.join('..', '..', '..','samples', 'sami.jpg')
#BROKEN_IMAGE_FILENAME = os.path.join('..', '..', '..','samples', 'brokenImage.jpg')
JPG_SAMPLE_IMAGE_FILENAME = os.path.join('..','samples', 'sami.jpg')
BROKEN_IMAGE_FILENAME = os.path.join('..', 'brokenImage.jpg')
JPG_SAMPLE_IMAGE_SIZE = (3264, 2448)

class ImageEngineTestsCase(support.AbstractIntegrationTestCase):
    
    def onSetUp(self):
        self._itemRepository = self._imageServerFactory.getItemRepository()
        self._persistenceProvider = self._imageServerFactory.getPersistenceProvider()
        self._template = self._persistenceProvider.session_template()
    
    def testImageIdShouldOnlyContainAlphanumericCharacters(self):
        try:
            self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId-')
        except imgengine.IDNotAuthorized, ex:
            assert ex.imageId == 'sampleId-'
    
    def testSaveBrokenImageShouldThrowException(self):
        try:
            self._imgProcessor.saveFileToRepository(BROKEN_IMAGE_FILENAME, 'sampleId')
        except imgengine.ImageFileNotRecognized, ex:
            pass
    
    def testSaveImageWithExistingIDShouldThrowException(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        try:
            self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')    
        except imgengine.ImageIDAlreadyExistingException, ex:
            assert ex.imageId == 'sampleId'
    
    def testSaveImageShouldUpdateFileSystemAndDatabase(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')) == True
        
        item = self._itemRepository.findOriginalItemById('sampleId')
        assert item is not None
        assert item.id == 'sampleId'
        assert item.format == domain.IMAGE_FORMAT_JPEG
        assert item.size == JPG_SAMPLE_IMAGE_SIZE
        assert item.status == domain.STATUS_OK
        
    def testPrepareTransformationWithNonExistingOriginalIdShouldThrowException(self):
        try:
            request = imgengine.TransformationRequest('nonexisting', (100,100), domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
    
    def testPrepareRequestShouldUpdateFileSystemAndDatabase(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        request = imgengine.TransformationRequest('sampleId', (100,100), domain.IMAGE_FORMAT_JPEG)
        result = self._imgProcessor.prepareTransformation(request)
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'sampleId-100x100.jpg')) == True
        
        item = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('sampleId', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert item is not None
        assert item.id == 'sampleId-100x100-JPEG'
        assert item.format == domain.IMAGE_FORMAT_JPEG
        assert item.size == (100,100)
        assert item.status == domain.STATUS_OK
        assert item.originalItem.id == 'sampleId'
        
        # result should be consistent across calls (caching..)
        result2 = self._imgProcessor.prepareTransformation(request)
        assert result == os.path.join('cache', 'sampleId-100x100.jpg')
        assert result2 == os.path.join('cache', 'sampleId-100x100.jpg')
    
    def testCleanUpShouldDeleteBothOriginalAndDerivedItemsThatAreInconsistent(self):
        
        # create 10 original items and 4 derived items per original items 
        for i in range(1,11):
            self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'item%s' %i)
         
            for size in [(100,100), (200,200), (300,300), (400,400)]:
                request = imgengine.TransformationRequest('item%s' % i, size, domain.IMAGE_FORMAT_JPEG)
                self._imgProcessor.prepareTransformation(request)
        
        # now mark 5 of the original items as inconsistent, as well as their associated derived items
        def mark_original_items_as_inconsistent(itemNumber):
            item = self._itemRepository.findOriginalItemById('item%s' % itemNumber)
            for di in item.derivedItems:
                di.status = domain.STATUS_INCONSISTENT
                self._itemRepository.update(di)
            item.status = domain.STATUS_INCONSISTENT
            self._itemRepository.update(item)
        
        for i in range(1,6):
            def callback(session):
                mark_original_items_as_inconsistent(i)
            self._template.do_with_session(callback)
            
        # finally, mark a few additional derived items as inconsistent, with their original item staying OK
        to_crush = [ self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('item6', (100,100),domain.IMAGE_FORMAT_JPEG),
                    self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('item6', (200,200),domain.IMAGE_FORMAT_JPEG),
                    self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('item6', (300,300),domain.IMAGE_FORMAT_JPEG),
                    self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('item6', (400,400),domain.IMAGE_FORMAT_JPEG) ]
        for item in to_crush:
            item.status = domain.STATUS_INCONSISTENT
            self._itemRepository.update(item)
        
        self._imgProcessor.cleanupInconsistentItems()
        
        # items 1 to 5 should not exist anymore (DB and file)
        for i in range(1,6):
            item = self._itemRepository.findOriginalItemById('item%s' % i)
            assert item is None
            assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'item%s.jpg' %(i))) == False
        
        # items 6 to 10 should still be OK
        for i in range(6,11):
            item = self._itemRepository.findOriginalItemById('item%s' % i)
            assert item is not None
            assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'item%s.jpg' %(i))) == True 
        
        # a few Derived Items that should be KO
        assert self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('item6', (100,100),domain.IMAGE_FORMAT_JPEG) is None
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'item6-100x100.jpg')) == False
        assert self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('item6', (200,200),domain.IMAGE_FORMAT_JPEG) is None
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'item6-200x200.jpg')) == False
        
        # a few Derived Items that should be OK
        assert self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('item7', (200,200),domain.IMAGE_FORMAT_JPEG) is not None
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'item7-200x200.jpg')) == True
    
    def koImageRequestProcessorMultithreadedTestCase(self):
        
        children = []
        for i in range(NB_THREADS):
            currentThread = SaveImageToRepositoryThread(self._imgProcessor, "sami%s" %(i))
            currentThread.start()
            children.append(currentThread)
        
        #Randomize sleeping float , 0.0 <= x < 1.0
        #time.sleep(random.random())
        #time.sleep(2)
        
        k = 0
        for thread in children:
            thread.join()
            assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sami%s.jpg' %(k))) == True
            k=k+1
    
    

class SaveImageToRepositoryThread(Thread):
    def __init__ (self, imgProcessor, itemid):
        Thread.__init__(self)
        self.__imgProcessor = imgProcessor
        self.__itemid = itemid


    def run(self):
            self.__imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, self.__itemid)

        
    
def suite():
    return unittest.makeSuite(ImageEngineTestsCase, 'test')
