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

_CACHE_DIRECTORY = "cache"
_ORIGINAL_DIRECTORY = "pictures"

class NestedPathGenerator(object):
    """ a resources.PathGenerator implementation that uses nested directories to reduce the number of files in the same directory """
    implements(resources.PathGenerator)
    def __init__(self, image_format_mapper, data_directory):
        self.__image_format_mapper = resources.ImageFormatMapper(image_format_mapper)
        self.__data_directory = data_directory
    
    def __extension_for_format(self, format):
        return self.__image_format_mapper.format_to_extension(format)
    
    def original_path(self, original_image_metadata):
        """ 
            the hash is computed on the ID only
            @returns /original/72/bc/45/..../2d/72bc4503be82feec7382057970e78092fb12ddd2.jpg """
        return resources.Path(self.__data_directory) \
            .append(_ORIGINAL_DIRECTORY) \
            .appendall(self._split(self._hash(original_image_metadata.id))) \
            .append('%s.%s' % (self._hash(original_image_metadata.id),
                               self.__extension_for_format(original_image_metadata.format)))
    
    def derived_path(self, derived_image_metadata):
        """ 
            The hash is computed on the complete derived filename
            @returns /derived/78/55/...../64/78552c5560bdbbd6344800a92d085faa7e286419-100x100.jpg """
        return resources.Path(self.__data_directory) \
            .append(_CACHE_DIRECTORY) \
            .appendall(self._split(self._hash(self._derived_image_filename_without_extension(derived_image_metadata)))) \
            .append(self._derived_image_filename(derived_image_metadata))
    
    def _derived_image_filename(self, derived_image_metadata):
        """ computes a hash on top of the full derived filename, and still add the size and extension to the final name"""
        return '%s-%sx%s.%s' % (self._hash(self._derived_image_filename_without_extension(derived_image_metadata)),
                                derived_image_metadata.size[0],
                                derived_image_metadata.size[1],
                                self.__extension_for_format(derived_image_metadata.format))
    
    def _derived_image_filename_without_extension(self, derived_image_metadata):
        return '%s-%sx%s.%s' % (derived_image_metadata.original_image_metadata.id,
                             derived_image_metadata.size[0],
                             derived_image_metadata.size[1],
                             self.__extension_for_format(derived_image_metadata.format))
        
    def _hash(self, image_id):
        h = hashlib.sha1()
        h.update(image_id)
        return h.hexdigest()

    def _split(self, image_id):
        import math
        # v = value to split, l = size of each chunk
        f = lambda v, l: [v[i * l:(i + 1) * l] for i in range(int(math.ceil(len(v) / float(l))))]
        return f(image_id[:-2], 2)
