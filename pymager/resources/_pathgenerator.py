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

class PathGenerator(Interface):
    def original_path(self, original_image_metadata):
        """returns a Path object for the given original item"""
    
    def derived_path(self, derived_image_metadata):
        """ returns a Path object for the given derived item"""
