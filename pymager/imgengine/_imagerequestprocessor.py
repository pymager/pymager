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

class ImageRequestProcessor(Interface):
    """ Processes ImageRequest objects and does the required work to prepare the images """
    
    def get_original_image_path(self, image_id):
        """@return: the relative path of the original image that has the given image_id 
        @rtype: str
        @raise imgengine.ImageMetadataNotFoundException: if image_id does not exist"""
        
    def save_file_to_repository(self, file, image_id):
        """ save the given file to the image server repository. 
        It will then be available for transformations
        @param file: either a filename or a file-like object 
        that is opened in binary mode
        @raise imgengine.ImageIDAlreadyExistsException 
        @raise imgengine.ImageStreamNotRecognizedException
        @raise imgengine.ImageProcessingException if unknown exceptions happen during the save process
        """
    
    def prepare_transformation(self, transformationRequest):
        """ Takes an ImageRequest and prepare the output for it. 
        Updates the database so that it is in sync with the filesystem
        @return: the path to the generated file (relative to the data directory)
        @raise imgengine.ImageMetadataNotFoundException: if image_id does not exist
        @raise imgengine.ImageProcessingException in case of any non-recoverable error 
        """
    
    def delete(self, image_id):
        """ Deletes the given item, and its associated item (in the case of an original 
        item that has derived items based on it)
        @raise imgengine.ImageMetadataNotFoundException: if image_id does not exist
        """
    
    def cleanup_inconsistent_items(self):
        """ deletes the files and items whose status is not OK (startup cleanup)"""
