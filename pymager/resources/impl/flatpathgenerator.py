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
import hashlib
from zope.interface import implements
from pymager import resources


CACHE_DIRECTORY = "cache"
ORIGINAL_DIRECTORY = "pictures"

class FlatPathGenerator(object):
    implements(resources.PathGenerator)
    def __init__(self, image_format_mapper, data_directory):
        self.__image_format_mapper = resources.ImageFormatMapper(image_format_mapper)
        self.__data_directory = data_directory
    
    def __extension_for_format(self, format):
        return self.__image_format_mapper.format_to_extension(format)
    
    def original_path(self, original_image_metadata):
        return resources.Path(self.__data_directory).append(ORIGINAL_DIRECTORY).append('%s.%s' % (self._hash(original_image_metadata.id), self.__extension_for_format(original_image_metadata.format)))
    
    def derived_path(self, derived_image_metadata):
        return resources.Path(self.__data_directory).append(CACHE_DIRECTORY).append('%s-%sx%s.%s' % (self._hash(derived_image_metadata.original_image_metadata.id), derived_image_metadata.size[0], derived_image_metadata.size[1], self.__extension_for_format(derived_image_metadata.format)))
   
    def _hash(self, image_id):
        h = hashlib.sha1()
        h.update(image_id)
        return h.hexdigest()
