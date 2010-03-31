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

import unittest
from pymager.resources.impl.pilimageformatmapper import PilImageFormatMapper
from tests.pymagertests import assertionutils

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
                    
