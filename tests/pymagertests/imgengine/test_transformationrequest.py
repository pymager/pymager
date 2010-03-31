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
import mox
from mox import IgnoreArg
from pymager import imgengine
from pymager import resources

class TransformationRequestTestCase(unittest.TestCase):    
    def setUp(self):
        self.mox = mox.Mox()
        pass
    
    def test_should_create_transformation_request(self):
        image_mapper = self.mox.CreateMockAnything()
        image_mapper.__conform__(IgnoreArg()).InAnyOrder().AndReturn(image_mapper)
        image_mapper.supports_format("JPEG").AndReturn(True)
        self.mox.ReplayAll()
         
        transformation_request = imgengine.TransformationRequest(image_mapper, "myimage", (800, 600), "JPEG")
        self.assertEquals("myimage", transformation_request.image_id)
        self.assertEquals((800, 600), transformation_request.size)
        self.assertEquals("JPEG", transformation_request.target_format)
        
        self.mox.VerifyAll()
        
    def test_should_check_that_format_is_supported(self):
        image_mapper = self.mox.CreateMockAnything()
        image_mapper.__conform__(IgnoreArg()).InAnyOrder().AndReturn(image_mapper)
        image_mapper.supports_format("PIXAR").AndReturn(False)
        self.mox.ReplayAll()
         
        try:
            imgengine.TransformationRequest(image_mapper, "myimage", (800, 600), "PIXAR")
        except imgengine.ImageFormatNotSupportedException, e:
            self.assertEquals("PIXAR", e.image_format)
        
        self.mox.VerifyAll()
