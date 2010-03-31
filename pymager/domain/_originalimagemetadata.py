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

from pymager.domain._abstractimagemetadata import AbstractImageMetadata

class OriginalImageMetadata(AbstractImageMetadata):
    def __init__(self, itemId, status, size, format):
        assert itemId is not None
        super(OriginalImageMetadata, self).__init__(itemId, status, size, format)
    
    def associated_image_path(self, path_generator):
        return path_generator.original_path(self)
