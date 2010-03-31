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

from pymager.imgengine._imageprocessingexception import ImageProcessingException

class ImageIDAlreadyExistsException(ImageProcessingException):
    def __init__(self, image_id):
        super(ImageIDAlreadyExistsException, self).__init__('An image with the given ID already exists in the repository: %s' % image_id)
        self.image_id = image_id
