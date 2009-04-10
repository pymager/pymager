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
from imgserver.web.deriveditemurldecoder import DerivedItemUrlDecoder,UrlDecodingError

class DerivedItemUrlDecoderTestCase(unittest.TestCase):
        
    def testShouldBeAbleToDecodeUrlSegment(self):
        url_segment = 'item123-800x600.JPEG'
        decoded = DerivedItemUrlDecoder(url_segment)
        self.assertEqual('item123', decoded.itemid)
        self.assertEqual(800, decoded.width)
        self.assertEqual(600, decoded.height)
        self.assertEqual('JPEG', decoded.format)
    
    def testFormatShouldBeUppercased(self):
        url_segment = 'item123-800x600.jpeg'
        decoded = DerivedItemUrlDecoder(url_segment)
        self.assertEqual('JPEG', decoded.format)
    
    def testBadUrlSegmentShouldThrowException(self):
        try:
            decoded = DerivedItemUrlDecoder('item123800x600.jpg')
            self.fail()
        except UrlDecodingError:
            pass

def suite():
    return unittest.TestSuite(unittest.makeSuite(DerivedItemUrlDecoderTestCase, 'test'))