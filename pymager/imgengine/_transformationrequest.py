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

from pymager.imgengine._imageformatnotsupportedexception import ImageFormatNotSupportedException 

from pymager.resources import ImageFormatMapper

class TransformationRequest(object):
    """ Stores the parameters of an image processing request """
    def __init__(self, image_format_mapper, image_id, size, target_format):
        """ @param size: a (width, height) tuple
            @raise ImageFormatNotSupportedException: when the given format is not supported by the underlying image_format_mapper
        """
        self._image_format_mapper = ImageFormatMapper(image_format_mapper)
        if not self._image_format_mapper.supports_format(target_format):
            raise ImageFormatNotSupportedException(target_format)
        
        self.image_id = image_id
        self.size = size
        self.target_format = target_format

    def __str__(self):
        return "TransformationRequest: %s %s %s" % (self.image_id, self.size, self.target_format)