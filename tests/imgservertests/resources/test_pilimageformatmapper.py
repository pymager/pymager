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
import unittest
from imgserver.resources.impl.pilimageformatmapper import PilImageFormatMapper
from tests.imgservertests import assertionutils

class PilImageFormatMapperTestCase(unittest.TestCase):
    def setUp(self):
        self._image_format_mapper = PilImageFormatMapper()
    def test_should_support_jpeg_format(self):
        self.assertTrue(self._image_format_mapper.supports_format('JPEG'))
    def test_support_format_should_be_case_sensitive(self):
        self.assertFalse(self._image_format_mapper.supports_format('jpeg'))
    def test_should_support_jpg_extension(self):
        self.assertTrue(self._image_format_mapper.supports_extension('jpg'))
    def test_should_support_jpeg_extension(self):
        self.assertTrue(self._image_format_mapper.supports_extension('jpeg'))
    def test_extension_to_format_should_lookup_map_for_known_types(self):
        self.assertEquals('JPEG', self._image_format_mapper.extension_to_format('jpg'))
    def test_extension_to_format_should_uppercase_for_unknown_types(self):
        self.assertEquals('PIXAR', self._image_format_mapper.extension_to_format('pixar'))
    def test_format_to_extension_should_lookup_map_for_known_extensions(self):
        self.assertEquals('jpg', self._image_format_mapper.format_to_extension('JPEG'))    
    def test_format_to_extension_should_lowercase_for_unknown_extensions(self):
        self.assertEquals('pixar', self._image_format_mapper.format_to_extension('PIXAR'))    
                    