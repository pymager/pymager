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
class SecurityCheckException(Exception):
    """Thrown when security requirements are not met while processing images """
    def __init__(self, message):
        Exception.__init__(self, message)

def image_transformation_security_decorator(authorized_sizes):
    """ Throws an exception if the decorated method receives a 
    tranformation request with a wrong size"""
    def decorator(func):
        def wrapper(transformation_request):
            if authorized_sizes is not None and not transformation_request.size in authorized_sizes:
                raise SecurityCheckException('Requested size is not allowed')
            return func(transformation_request)
        return wrapper
    return decorator