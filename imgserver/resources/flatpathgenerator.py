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
from zope.interface import implements
from imgserver.resources.path import Path
from imgserver.resources.pathgenerator import PathGenerator

CACHE_DIRECTORY = "cache"
ORIGINAL_DIRECTORY = "pictures"

FORMAT_EXTENSIONS = { "JPEG" : "jpg" }

class FlatPathGenerator(object):
    implements(PathGenerator)
    def __init__(self, data_directory):
        self.__data_directory = data_directory
    
    def __extension_for_format(self, format):
        return FORMAT_EXTENSIONS[format.upper()] if FORMAT_EXTENSIONS.__contains__(format.upper()) else format.lower()
    
    def original_path(self, original_item):
        return Path(self.__data_directory).append(ORIGINAL_DIRECTORY).append('%s.%s' % (original_item.id, self.__extension_for_format(original_item.format)))
    
    def derived_path(self, derived_item):
        return Path(self.__data_directory).append(CACHE_DIRECTORY).append('%s-%sx%s.%s' % (derived_item.original_item.id, derived_item.size[0], derived_item.size[1],self.__extension_for_format(derived_item.format)))
   