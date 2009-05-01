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
import exceptions
import unittest
from imgserver.web._derivedimagemetadataurldecoder import DerivedImageMetadataUrlDecoder
from imgserver.web._derivedimagemetadataurldecoder import UrlDecodingError
from tests.imgservertests import resources as testresources
import mox
from mox import IgnoreArg

class DerivedImageMetadataUrlDecoderTestCase(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()
        
    def test_should_decode_url_segment(self):
        url_segment = 'item123-800x600.jpg'
        decoded = DerivedImageMetadataUrlDecoder(testresources.FakeImageFormatMapper(), url_segment)
        self.assertEqual('item123', decoded.itemid)
        self.assertEqual(800, decoded.width)
        self.assertEqual(600, decoded.height)
        self.assertEqual('JPEG', decoded.format)
    
    def test_format_should_be_retrieved_using_image_mapper(self):
        image_mapper = self.mox.CreateMockAnything()
        image_mapper.__conform__(IgnoreArg()).InAnyOrder().AndReturn(image_mapper)
        image_mapper.extension_to_format("jpg").InAnyOrder().AndReturn("JPEG")
        self.mox.ReplayAll()
        
        url_segment = 'item123-800x600.jpg'
        decoded = DerivedImageMetadataUrlDecoder(image_mapper, url_segment)
        self.assertEqual('JPEG', decoded.format)
        self.mox.VerifyAll()
    
    def test_should_detect_bad_url(self):
        try:
            decoded = DerivedImageMetadataUrlDecoder(testresources.FakeImageFormatMapper(), 'item123800x600.jpg')
            self.fail()
        except UrlDecodingError:
            pass
