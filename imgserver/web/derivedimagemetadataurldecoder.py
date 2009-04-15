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
import re

# itemId-800x600.jpg
FILENAME_REGEX = re.compile(r'([a-zA-Z\d]+)\-(\d+)x(\d+)\.([a-zA-Z]+)')

class UrlDecodingError(Exception):
    def __init__(self, url_segment):
        self.url_segment = url_segment

class DerivedImageMetadataUrlDecoder(object):
    def __init__(self, url_segment):
        super(DerivedImageMetadataUrlDecoder, self).__init__()
        match = FILENAME_REGEX.match(url_segment)
        if match and len(match.groups()) == 4:
            self.itemid = match.group(1)
            self.width = int(match.group(2))
            self.height = int(match.group(3))
            self.format = match.group(4).upper()
        else:
            raise UrlDecodingError(url_segment)