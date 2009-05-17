# -*- coding: utf-8 -*-
"""
    PyMager RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of PyMager.

    PyMager is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyMager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with PyMager.  If not, see <http://www.gnu.org/licenses/>.

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
