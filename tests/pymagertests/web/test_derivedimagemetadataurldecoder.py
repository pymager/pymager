# -*- coding: utf-8 -*-
"""
   Copyright 2010 Sami Dalouche

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import exceptions
import unittest
from pymager.web._derivedimagemetadataurldecoder import DerivedImageMetadataUrlDecoder
from pymager.web._derivedimagemetadataurldecoder import UrlDecodingError
from tests.pymagertests import resources as testresources
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
        
    def test_should_decode_url_segment_when_id_contains_hyphens(self):
        url_segment = 'a-complex-id-with-hyphens-800x600.jpg'
        decoded = DerivedImageMetadataUrlDecoder(testresources.FakeImageFormatMapper(), url_segment)
        self.assertEqual('a-complex-id-with-hyphens', decoded.itemid)
        self.assertEqual(800, decoded.width)
        self.assertEqual(600, decoded.height)
        self.assertEqual('JPEG', decoded.format)
    
    def test_should_decode_url_segment_when_id_contains_underscores(self):
        url_segment = 'a_complex_id_with_underscores-800x600.jpg'
        decoded = DerivedImageMetadataUrlDecoder(testresources.FakeImageFormatMapper(), url_segment)
        self.assertEqual('a_complex_id_with_underscores', decoded.itemid)
        self.assertEqual(800, decoded.width)
        self.assertEqual(600, decoded.height)
        self.assertEqual('JPEG', decoded.format)
    
    def test_should_not_decode_url_segment_when_id_contains_non_ascii_characters(self):
        try:
            DerivedImageMetadataUrlDecoder(testresources.FakeImageFormatMapper(), 'éèàâùû-800x600.jpg')
            self.fail()
        except UrlDecodingError:
            pass
    
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
