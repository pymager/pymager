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
         
        transformation_request = imgengine.TransformationRequest(image_mapper, "myimage",(800,600), "JPEG" )
        self.assertEquals("myimage", transformation_request.image_id)
        self.assertEquals((800,600), transformation_request.size)
        self.assertEquals("JPEG", transformation_request.target_format)
        
        self.mox.VerifyAll()
        
    def test_should_check_that_format_is_supported(self):
        image_mapper = self.mox.CreateMockAnything()
        image_mapper.__conform__(IgnoreArg()).InAnyOrder().AndReturn(image_mapper)
        image_mapper.supports_format("PIXAR").AndReturn(False)
        self.mox.ReplayAll()
         
        try:
            imgengine.TransformationRequest(image_mapper, "myimage",(800,600), "PIXAR" )
        except imgengine.ImageFormatNotSupportedException, e:
            self.assertEquals("PIXAR", e.image_format)
        
        self.mox.VerifyAll()