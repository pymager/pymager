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
from pymager.domain._abstractimagemetadata import AbstractImageMetadata 

class DerivedImageMetadata(AbstractImageMetadata):
    def __init__(self, status, size, format, original_image_metadata):
        assert original_image_metadata is not None
        self._original_image_metadata = original_image_metadata
        
        super(DerivedImageMetadata, self).__init__("%s-%sx%s-%s" % (original_image_metadata.id, size[0], size[1], format),status, size, format)

    def get_original_image_metadata(self):
        return self._original_image_metadata
    
    def associated_image_path(self, path_generator):
        return path_generator.derived_path(self)
    
    original_image_metadata = property(get_original_image_metadata, None, None, None)