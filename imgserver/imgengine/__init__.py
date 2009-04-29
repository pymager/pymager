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
from imgserver.imgengine._imageprocessingexception import ImageProcessingException
from imgserver.imgengine._illegalimageidexception import IllegalImageIdException
from imgserver.imgengine._imageformatnotrecognizedexception import ImageFormatNotRecognizedException
from imgserver.imgengine._imageidalreadyexistsexception import ImageIDAlreadyExistsException
from imgserver.imgengine._imagemetadatanotfoundexception import ImageMetadataNotFoundException
        
def checkid(image_id):
    if not image_id.isalnum():
        raise IllegalImageIdException(image_id)