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
class ImageProcessingException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, message):
        super(ImageProcessingException, self).__init__(message)
        
class IDNotAuthorized(ImageProcessingException):
    def __init__(self, image_id):
        super(IDNotAuthorized, self).__init__('ID contains non alpha numeric characters: %s' % (image_id,))
        self.image_id = image_id

class ImageFileNotRecognized(ImageProcessingException):
    def __init__(self, ex):
        super(ImageFileNotRecognized, self).__init__(ex)

class ImageIDAlreadyExistingException(ImageProcessingException):
    def __init__(self, image_id):
        super(ImageIDAlreadyExistingException, self).__init__('An image with the given ID already exists in the repository: %s' % image_id)
        self.image_id = image_id
        
def checkid(image_id):
    if not image_id.isalnum():
        raise IDNotAuthorized(image_id)