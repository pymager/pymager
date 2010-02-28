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
from pymager.domain._derivedimagemetadata import DerivedImageMetadata
from pymager.domain._originalimagemetadata import OriginalImageMetadata
from pymager.domain._imagemetadatarepository import ImageMetadataRepository
from pymager.domain._imagemetadatarepository import DuplicateEntryException
# The possible statuses of a domain object
STATUS_INCONSISTENT = 'INCONSISTENT'
STATUS_OK = 'OK'

IMAGE_FORMAT_JPEG = 'JPEG'
