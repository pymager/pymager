"""
    PyMager RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of PyMager.

    PyMager is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyMager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with PyMager.  If not, see <http://www.gnu.org/licenses/>.

"""
from pymager.domain._abstractimagemetadata import AbstractImageMetadata

class OriginalImageMetadata(AbstractImageMetadata):
    def __init__(self, itemId, status, size, format):
        assert itemId is not None
        super(OriginalImageMetadata, self).__init__(itemId, status, size, format)
    
    def associated_image_path(self, path_generator):
        return path_generator.original_path(self)