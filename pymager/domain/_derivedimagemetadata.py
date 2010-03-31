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

class DerivedImageMetadata(AbstractImageMetadata):
    def __init__(self, status, size, format, original_image_metadata):
        assert original_image_metadata is not None
        self._original_image_metadata = original_image_metadata
        
        super(DerivedImageMetadata, self).__init__("%s-%sx%s-%s" % (original_image_metadata.id, size[0], size[1], format), status, size, format)

    def get_original_image_metadata(self):
        return self._original_image_metadata
    
    def associated_image_path(self, path_generator):
        return path_generator.derived_path(self)
    
    original_image_metadata = property(get_original_image_metadata, None, None, None)
