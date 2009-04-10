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
        self._item_repository = self._imageServerFactory.item_repository
        self._schema_migrator = self._imageServerFactory.schema_migrator
        self._template = self._schema_migrator.session_template()
    
    def __assertSampleFileIsSavedCorrectly(self):
        assert os.path.exists(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')) == True
        self.assertEquals(os.path.getsize(JPG_SAMPLE_IMAGE_FILENAME), os.path.getsize(os.path.join(support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')))
            
    def testSaveImageShouldAcceptFileLikeObjectAsImageSource(self):
        with open(JPG_SAMPLE_IMAGE_FILENAME, 'rb') as fobj:
            self._image_server.saveFileToRepository(fobj, 'sampleId')
            
        self.__assertSampleFileIsSavedCorrectly()

    