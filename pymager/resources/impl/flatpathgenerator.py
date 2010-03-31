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
