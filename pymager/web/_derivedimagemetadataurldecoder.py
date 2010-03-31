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
