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
import re
from pymager import resources

# itemId-800x600.jpg
FILENAME_REGEX = re.compile(r'([\w_-]+)\-(\d+)x(\d+)\.([a-zA-Z]+)')

class UrlDecodingError(Exception):
    def __init__(self, url_segment):
        self.url_segment = url_segment

class DerivedImageMetadataUrlDecoder(object):
    def __init__(self, image_format_mapper, url_segment):
        super(DerivedImageMetadataUrlDecoder, self).__init__()
        self._image_format_mapper = resources.ImageFormatMapper(image_format_mapper)
        match = FILENAME_REGEX.match(url_segment)
        if match and len(match.groups()) == 4:
            self.itemid = match.group(1)
            self.width = int(match.group(2))
            self.height = int(match.group(3))
            self.format = self._image_format_mapper.extension_to_format(match.group(4))
            
            #try:
                #self.itemid.decode('ascii')
            #except UnicodeDecodeError:
                #raise UrlDecodingError(url_segment)
        else:
            raise UrlDecodingError(url_segment)