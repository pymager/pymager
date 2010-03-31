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
from pymager.domain._derivedimagemetadata import DerivedImageMetadata
from pymager.domain._originalimagemetadata import OriginalImageMetadata
from pymager.domain._imagemetadatarepository import ImageMetadataRepository
from pymager.domain._imagemetadatarepository import DuplicateEntryException
# The possible statuses of a domain object
STATUS_INCONSISTENT = 'INCONSISTENT'
STATUS_OK = 'OK'

IMAGE_FORMAT_JPEG = 'JPEG'
