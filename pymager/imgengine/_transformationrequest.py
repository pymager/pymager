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