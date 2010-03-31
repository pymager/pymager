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
from pymager.domain._abstractimagemetadata import AbstractImageMetadata
from pymager.domain._originalimagemetadata import OriginalImageMetadata
from pymager.domain._derivedimagemetadata import DerivedImageMetadata


class DuplicateEntryException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, duplicate_id):
        self.__duplicate_id = duplicate_id
        Exception.__init__(self, 'Duplicated ID: %s' % duplicate_id)

    def get_duplicate_id(self):
        return self.__duplicate_id
    
    duplicate_id = property(get_duplicate_id, None, None, "The ID that led to the DuplicateEntryException")

class ImageMetadataRepository(Interface):
    """ DDD repository for Original and Derived Items """
    def find_original_image_metadata_by_id(self, image_id):
        """ Find an OriginalImageMetadata by its ID """
    
    def find_inconsistent_original_image_metadatas(self, maxResults=100):
        """ Find Original Items that are in an inconsistent state """
    
    def find_inconsistent_derived_image_metadatas(self, maxResults=100):
        """ Find Derived Items that are in an inconsistent state """
    
    def find_derived_image_metadata_by_original_image_metadata_id_size_and_format(self, image_id, size, format):
        """ Find Derived Items By :
            - the Original Item ID
            - the size of the Derived Item
            - the format of the Derived Item """
    def add(self, item):
         """ Create a persistent instance of an item
             @raise DuplicateEntryException: when an item with similar characteristics has already been created   
         """
    def delete(self, item):
        """ Deletes an item, and its children items, in the case of an original item that has
        several derived items based on it"""
