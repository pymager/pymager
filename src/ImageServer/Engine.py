import Image, ImageOps
import mimetypes
import os, os.path, shutil

# Relative to the data_directory
CACHE_DIRECTORY = "cache"
ORIGINAL_DIRECTORY = "pictures"
FORMAT_EXTENSIONS = { "JPEG" : "jpg" }

# Layout
# data/original/image_id.format
# data/cache/image_id/800x600/format

def check_id(image_id):
    if not image_id.isalnum():
        raise ImageProcessingException, 'ID contains non alpha numeric characters: %s' % image_id
            
class ImageProcessingException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, message):
        Exception.__init__(self, message)

class TransformationRequest():
    """ Stores the parameters of an image processing request """
    def __init__(self, image_id, size, target_format):
        """ @param size: a (width, height) tuple
        """
        check_id(image_id)
        
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
            [self.__absolute_cache_directory(), self.__absolute_original_directory()]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
    def __absolute_cache_directory(self):
        """ @return: the directory that will be used for caching image processing 
        results """
        return '%s/%s' % (self.data_directory, CACHE_DIRECTORY)
    
    def __absolute_original_directory(self):
        """ @return. the directory that will be used to store original files, 
        before processing"""
        return '%s/%s' % (self.data_directory, ORIGINAL_DIRECTORY)
    
    def __absolute_original_filename(self, image_id):
        """ returns the filename of the original file """
        return "%s/%s" % (self.__absolute_original_directory(), image_id)
    
    def __absolute_cached_filename(self, image_id, size, format):
        return '%s/%s' % (  self.data_directory,
                            self.__relative_cached_filename(image_id, size, format))
    
    def __relative_cached_filename(self, image_id, size, format):
        """ relative to the base directory """
        return '%s/%s-%sx%s.%s' % ( CACHE_DIRECTORY, 
                                    image_id, 
                                    size[0], 
                                    size[1], 
                                    self.__extension_for_format(format))
        
    def __extension_for_format(self, format):
        return FORMAT_EXTENSIONS[format.upper()] if FORMAT_EXTENSIONS.__contains__(format.upper()) else format.lower()

    def save_file_to_repository(self, filename, image_id):
        """ save the given file to the image server repository. 
        It will then be available for transformations"""
        
        check_id(image_id)
        
        if os.path.exists(self.__absolute_original_filename(image_id)):
            raise ImageProcessingException, 'an image with the given ID already exists in the repository'
        
        # Check that the image is not broken
        Image.open(filename).verify()
        
        try:
            shutil.copyfile(filename, self.__absolute_original_filename(image_id))
        except IOError, ex:
            raise ImageProcessingException, ex
    
    def prepare_transformation(self, transformation_request):
        """ Takes an ImageRequest and prepare the output for it.
            @return: the path to the generated file (relative to the cache directory) 
            """
        cached_filename = self.__absolute_cached_filename(transformation_request.image_id, 
                                                 transformation_request.size, 
                                                 transformation_request.target_format)
        relative_cached_filename = self.__relative_cached_filename(transformation_request.image_id, 
                                               transformation_request.size, 
                                               transformation_request.target_format)

        if os.path.exists(cached_filename):
            return relative_cached_filename
        
        cached_filename = self.__absolute_cached_filename(transformation_request.image_id, 
                                                 transformation_request.size, 
                                                 transformation_request.target_format)
        original_filename = self.__absolute_original_filename(transformation_request.image_id)
        try:
            img = Image.open(original_filename)
        except IOError, ex: 
            raise ImageProcessingException, ex
        
        if transformation_request.size == img.size and transformation_request.target_format.upper() == img.format.upper():
            try:
                shutil.copyfile(self.__absolute_original_filename(transformation_request.image_id), 
                                cached_filename)
            except IOError, ex:
                raise ImageProcessingException, ex
        else:   
            target_image = ImageOps.fit(image=img, 
                                        size=transformation_request.size, 
                                        method=Image.ANTIALIAS,
                                        centering=(0.5,0.5)) 
            try:
                target_image.save(cached_filename)
            except IOError, ex:
                raise ImageProcessingException, ex
        
        return cached_filename
    
    

