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
from tests import support
from imgserver import imgengine, domain
from imgserver.imgengine.imagerequestprocessor import ItemDoesNotExistError
from imgserver.imgengine.transformationrequest import TransformationRequest
from pkg_resources import resource_filename


NB_THREADS = 15

#JPG_SAMPLE_IMAGE_FILENAME = os.path.join('..', '..', 'samples', 'sami.jpg')
#BROKEN_IMAGE_FILENAME = os.path.join('..', '..', 'samples', 'brokenImage.jpg')
JPG_SAMPLE_IMAGE_FILENAME = resource_filename('imgserver.samples', 'sami.jpg')
BROKEN_IMAGE_FILENAME = resource_filename('imgserver.samples', 'brokenImage.jpg')
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
            assert ex.image_id == 'sampleId-'
    
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
            assert ex.image_id == 'sampleId'
    
    def testSaveImageShouldUpdateFileSystemAndDatabase(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        self.__assertSampleFileIsSavedCorrectly()
        
        item = self._itemRepository.find_original_item_by_id('sampleId')
        assert item is not None
        assert item.id == 'sampleId'
        assert item.format == domain.IMAGE_FORMAT_JPEG
        assert item.size == JPG_SAMPLE_IMAGE_SIZE
        assert item.status == domain.STATUS_OK
    
    def __assertSampleFileIsSavedCorrectly(self):
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')) == True
        self.assertEquals(os.path.getsize(JPG_SAMPLE_IMAGE_FILENAME), os.path.getsize(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')))
            
    def testSaveImageShouldAcceptFileLikeObjectAsImageSource(self):
        with open(JPG_SAMPLE_IMAGE_FILENAME, 'rb') as fobj:
            self._imgProcessor.saveFileToRepository(fobj, 'sampleId')
            
        self.__assertSampleFileIsSavedCorrectly()
    
    def testPrepareTransformationWithNonExistingOriginalIdShouldThrowException(self):
        try:
            request = TransformationRequest('nonexisting', (100,100), domain.IMAGE_FORMAT_JPEG)
        except ItemDoesNotExistError, ex:
            self.assertEquals('nonexisting', ex.item_id)
    
    def testPrepareRequestShouldUpdateFileSystemAndDatabase(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        request = TransformationRequest('sampleId', (100,100), domain.IMAGE_FORMAT_JPEG)
        result = self._imgProcessor.prepareTransformation(request)
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'sampleId-100x100.jpg')) == True
        
        item = self._itemRepository.find_derived_item_by_original_item_id_size_and_format('sampleId', (100,100), domain.IMAGE_FORMAT_JPEG)
        assert item is not None
        assert item.id == 'sampleId-100x100-JPEG'
        assert item.format == domain.IMAGE_FORMAT_JPEG
        assert item.size == (100,100)
        assert item.status == domain.STATUS_OK
        assert item.original_item.id == 'sampleId'
        
        # result should be consistent across calls (caching..)
        result2 = self._imgProcessor.prepareTransformation(request)
        assert result == os.path.join('cache', 'sampleId-100x100.jpg')
        assert result2 == os.path.join('cache', 'sampleId-100x100.jpg')
    
    def testCleanUpShouldDeleteBothOriginalAndDerivedItemsThatAreInconsistent(self):
        
        # create 10 original items and 4 derived items per original items 
        for i in range(1,11):
            self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'item%s' %i)
         
            for size in [(100,100), (200,200), (300,300), (400,400)]:
                request = TransformationRequest('item%s' % i, size, domain.IMAGE_FORMAT_JPEG)
                self._imgProcessor.prepareTransformation(request)
        
        # now mark 5 of the original items as inconsistent, as well as their associated derived items
        def mark_original_items_as_inconsistent(itemNumber):
            item = self._itemRepository.find_original_item_by_id('item%s' % itemNumber)
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
        to_crush = [ self._itemRepository.find_derived_item_by_original_item_id_size_and_format('item6', (100,100),domain.IMAGE_FORMAT_JPEG),
                    self._itemRepository.find_derived_item_by_original_item_id_size_and_format('item6', (200,200),domain.IMAGE_FORMAT_JPEG),
                    self._itemRepository.find_derived_item_by_original_item_id_size_and_format('item6', (300,300),domain.IMAGE_FORMAT_JPEG),
                    self._itemRepository.find_derived_item_by_original_item_id_size_and_format('item6', (400,400),domain.IMAGE_FORMAT_JPEG) ]
        for item in to_crush:
            item.status = domain.STATUS_INCONSISTENT
            self._itemRepository.update(item)
        
        self._imgProcessor._cleanupInconsistentItems()
        
        # items 1 to 5 should not exist anymore (DB and file)
        for i in range(1,6):
            item = self._itemRepository.find_original_item_by_id('item%s' % i)
            assert item is None
            assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'item%s.jpg' %(i))) == False
        
        # items 6 to 10 should still be OK
        for i in range(6,11):
            item = self._itemRepository.find_original_item_by_id('item%s' % i)
            assert item is not None
            assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'item%s.jpg' %(i))) 
        
        # a few Derived Items that should be KO
        assert self._itemRepository.find_derived_item_by_original_item_id_size_and_format('item6', (100,100),domain.IMAGE_FORMAT_JPEG) is None
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'item6-100x100.jpg')) == False
        assert self._itemRepository.find_derived_item_by_original_item_id_size_and_format('item6', (200,200),domain.IMAGE_FORMAT_JPEG) is None
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'item6-200x200.jpg')) == False
        
        # a few Derived Items that should be OK
        assert self._itemRepository.find_derived_item_by_original_item_id_size_and_format('item7', (200,200),domain.IMAGE_FORMAT_JPEG) is not None
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'item7-200x200.jpg')) == True
    
    def testShouldReturnOriginalFilenameForExistingItem(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        path = self._imgProcessor.getOriginalImagePath('sampleId')
        self.assertTrue(os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, path)))
    
    def testReturnOriginalFilenameShouldRaiseExceptionWhenItemDoesNotExist(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        try:
            self._imgProcessor.getOriginalImagePath('anyItem')
            self.fail()
        except ItemDoesNotExistError, ex:
            self.assertEquals('anyItem', ex.item_id)
        
    def testOriginalImageShouldExist(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        self.assertTrue(self._imgProcessor.originalImageExists('sampleId'))
    
    def testOriginalImageShouldNotExist(self):
        self.assertFalse(self._imgProcessor.originalImageExists('sampleId'))
        
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
