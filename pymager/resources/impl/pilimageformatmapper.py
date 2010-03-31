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

from zope.interface import Interface, implements
from pymager import resources

SUPPORTED_FORMATS = ["BMP", "EPS", "GIF", "IM", "JPEG", "MSP", "PALM", "PCX", "PDF", "PNG", "PPM", "TIFF", "XBM", "XV"]
FORMATS_TO_EXTENSIONS = { "JPEG" : "jpg" }

# create another map to simulate bidirectional map
EXTENSIONS_TO_FORMATS = {}
for f in FORMATS_TO_EXTENSIONS:
    EXTENSIONS_TO_FORMATS[FORMATS_TO_EXTENSIONS[f]] = f
    

class PilImageFormatMapper(object):
    implements(resources.ImageFormatMapper)
    def __init__(self):
        pass
    
    def supports_format(self, format):
        return format in SUPPORTED_FORMATS
    
    def supports_extension(self, extension):
        return self.supports_format(self.extension_to_format(extension))
    
    def extension_to_format(self, extension):
        return EXTENSIONS_TO_FORMATS[extension.lower()] if extension.lower() in EXTENSIONS_TO_FORMATS else extension.upper()
    
    def format_to_extension(self, format):
        return FORMATS_TO_EXTENSIONS[format.upper()] if format.upper() in FORMATS_TO_EXTENSIONS else format.lower()
    
