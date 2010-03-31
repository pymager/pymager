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

class ImageFormatMapper(Interface):
    def supports_format(self, format):
        """ @return:  a boolean indicating whether the given format is supported """
    
    def supports_extension(self, extension):
        """ @return: a boolean indicating if whether the given format is supported"""
    
    def extension_to_format(self, extension):
        """ converts an extension (string) to a standardized format name (string)"""
    
    def format_to_extension(self, format):
        """ converts a format (string) to an extension (string)"""
