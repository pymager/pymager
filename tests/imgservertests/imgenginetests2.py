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
    
    def __assertSampleFileIsSavedCorrectly(self):
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')) == True
        self.assertEquals(os.path.getsize(JPG_SAMPLE_IMAGE_FILENAME), os.path.getsize(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')))
            
    def testSaveImageShouldAcceptFileLikeObjectAsImageSource(self):
        with open(JPG_SAMPLE_IMAGE_FILENAME, 'rb') as fobj:
            self._imgProcessor.saveFileToRepository(fobj, 'sampleId')
            
        self.__assertSampleFileIsSavedCorrectly()

    