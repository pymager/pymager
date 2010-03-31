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

import os.path
import unittest
from pymager.resources.impl.nestedpathgenerator import NestedPathGenerator
from tests.pymagertests.resources.fake_image_format_mapper import FakeImageFormatMapper
from tests.pymagertests import objectmothers
from pymager import domain

class NestedPathGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self._path_generator = NestedPathGenerator(FakeImageFormatMapper(), os.path.abspath("/basedir"))
    
    def test_should_return_original_image_path(self):
        self.assertEquals(
            os.path.abspath("/basedir/pictures/66/b1/fb/ce/ca/25/b9/95/78/0a/7a/6f/8f/ea/79/b6/97/ce/cc/66b1fbceca25b995780a7a6f8fea79b697ceccb0.jpg"),
            self._path_generator.original_path(objectmothers.original_yemmagouraya_metadata()).absolute())
        
    def test_should_return_derived_image_path(self):
        self.assertEquals(
            os.path.abspath("/basedir/cache/d8/ae/48/bd/0c/62/ea/68/2c/df/e5/26/ce/df/68/6a/48/04/5a/d8ae48bd0c62ea682cdfe526cedf686a48045a7d-100x100.jpg"),
            self._path_generator.derived_path(objectmothers.derived_100x100_yemmagouraya_metadata()).absolute())
   
