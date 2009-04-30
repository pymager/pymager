from zope.interface import Interface, implements

class ImageRequestProcessor(Interface):
    """ Processes ImageRequest objects and does the required work to prepare the images """
    
    def supports_format(self, output_format):
        """
        @param output_format: a String that represents an image format (e.g. JPEG) 
        @return whether the given output_format is supported
        """
    
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
        @raise imgengine.ImageFormatNotRecognizedException
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
