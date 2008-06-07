import Image, ImageOps
import mimetypes
import os, os.path, shutil

# Relative to the data_directory
CACHE_DIRECTORY = "cache"
ORIGINAL_DIRECTORY = "original"

# Layout
# data/original/image_id.format
# data/cache/image_id/800x600/format
 

class ImageProcessingException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, message):
        Exception.__init__(self, message)

class TransformationRequest():
    """ Stores the parameters of an image processing request """
    def __init__(self, image_id, size, target_format):
        """ @param size: a (width, height) tuple
        """
        self.image_id = image_id
        self.size = size
        self.target_format = target_format

class ImageRequestProcessor():
    """ Processes ImageRequest objects and does the required work to prepare the images """
    def __init__(self, data_directory):
        """ @param data_directory: the directory that this 
            ImageRequestProcessor will use for its work files """
        self.data_directory = data_directory 
        self.__init_directories()

    def __init_directories(self):
        """ Creates the work directories needed to run this processor """
        for directory in \
            [self.__cache_directory(), self.__original_directory()]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
    def __cache_directory(self):
        """ @return: the directory that will be used for caching image processing 
        results """
        return '%s/%s' % (self.data_directory, CACHE_DIRECTORY)
    
    def __original_directory(self):
        """ @return. the directory that will be used to store original files, 
        before processing"""
        return '%s/%s' % (self.data_directory, ORIGINAL_DIRECTORY)
    
    def __original_filename(self, image_id):
        """ returns the filename of the original file """
        return "%s/%s" % (self.__original_directory(), image_id)
    
    def save_file_to_repository(self, filename, image_id):
        """ save the given file to the image server repository. 
        It will then be available for transformations"""
        try:
            shutil.copyfile(filename, self.__original_filename(image_id))
        except IOError, ex:
            raise ImageProcessingException, ex
    
    def prepare_transformation(self, image_request):
        """ Takes an ImageRequest and prepare the output for it.
            @return: nothing for now... The prepared image will be available in data_directory/cache
            """ 
        img = Image.open('../samples/%s.jpg' % image_request.image_id)
        target_image = ImageOps.fit(image=img, 
                                    size=image_request.size, 
                                    centering=(0.5,0.5))
        try:
            target_image.save('%s/%s-%sx%s.%s' % (  self.__cache_directory(),
                                                     image_request.image_id, 
                                                     image_request.size[0], 
                                                     image_request.size[1], 
                                                     image_request.target_format))
        except IOError, ex:
            raise ImageProcessingException, ex

