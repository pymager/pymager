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
from zope.interface import Interface, implements
from pymager import resources

class FakeImageFormatMapper(object):
    implements(resources.ImageFormatMapper)
    def __init__(self):
        pass
    
    def supports_format(self, format):
        return True
    
    def supports_extension(self, extension):
        return True
    
    def extension_to_format(self, extension):
        return 'JPEG'
    
    def format_to_extension(self, format):
        return 'jpg'
    
