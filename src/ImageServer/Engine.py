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

def checkid(imageId):
    if not imageId.isalnum():
        raise ImageProcessingException, 'ID contains non alpha numeric characters: %s' % imageId
            
class ImageProcessingException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, message):
        Exception.__init__(self, message)

class TransformationRequest():
    """ Stores the parameters of an image processing request """
    def __init__(self, image_id, size, target_format):
        """ @param size: a (width, height) tuple
        """
        checkid(image_id)
        
        self.image_id = image_id
        self.size = size
        self.target_format = target_format

class ImageRequestProcessor():
    
    """ Processes ImageRequest objects and does the required work to prepare the images """
    def __init__(self, itemRepository, dataDirectory):
        """ @param data_directory: the directory that this 
            ImageRequestProcessor will use for its work files """
        self.__dataDirectory = dataDirectory 
        self.__initDirectories()
        self.__itemRepository = itemRepository
        
    def __initDirectories(self):
        """ Creates the work directories needed to run this processor """
        for directory in \
            [self.__absoluteCacheDirectory(), self.__absoluteOriginalDirectory()]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
    def __absoluteCacheDirectory(self):
        """ @return: the directory that will be used for caching image processing 
        results """
        return os.path.join(self.__dataDirectory, CACHE_DIRECTORY)
    
    def __absoluteOriginalDirectory(self):
        """ @return. the directory that will be used to store original files, 
        before processing"""
        return os.path.join (self.__dataDirectory, ORIGINAL_DIRECTORY)
    
    def __absoluteOriginalFilename(self, image_id):
        """ returns the filename of the original file """
        return os.path.join (self.__absoluteOriginalDirectory(), image_id)
    
    def __absoluteCachedFilename(self, image_id, size, format):
        
        return os.path.join( self.__dataDirectory,
                            self.__relativeCachedFilename(image_id, size, format))
    
    def __relativeCachedFilename(self, image_id, size, format):
        """ relative to the base directory """
        return os.path.join ( CACHE_DIRECTORY, 
                              '%s-%sx%s.%s' % (image_id, size[0], size[1],self.__extensionForFormat(format)) )
        
    def __extensionForFormat(self, format):
        return FORMAT_EXTENSIONS[format.upper()] if FORMAT_EXTENSIONS.__contains__(format.upper()) else format.lower()

    def saveFileToRepository(self, filename, image_id):
        """ save the given file to the image server repository. 
        It will then be available for transformations"""
        
        checkid(image_id)
        
        if os.path.exists(self.__absoluteOriginalFilename(image_id)):
            raise ImageProcessingException, 'an image with the given ID already exists in the repository'
        
        # Check that the image is not broken
        Image.open(filename).verify()
        
        try:
            shutil.copyfile(filename, self.__absoluteOriginalFilename(image_id))
        except IOError, ex:
            raise ImageProcessingException, ex
    
    def prepareTransformation(self, transformation_request):
        """ Takes an ImageRequest and prepare the output for it.
            @return: the path to the generated file (relative to the cache directory) 
            """
        cached_filename = self.__absoluteCachedFilename(transformation_request.image_id, 
                                                 transformation_request.size, 
                                                 transformation_request.target_format)
        relative_cached_filename = self.__relativeCachedFilename(transformation_request.image_id, 
                                               transformation_request.size, 
                                               transformation_request.target_format)

        if os.path.exists(cached_filename):
            return relative_cached_filename
        
        cached_filename = self.__absoluteCachedFilename(transformation_request.image_id, 
                                                 transformation_request.size, 
                                                 transformation_request.target_format)
        original_filename = self.__absoluteOriginalFilename(transformation_request.image_id)
        try:
            img = Image.open(original_filename)
        except IOError, ex: 
            raise ImageProcessingException, ex
        
        if transformation_request.size == img.size and transformation_request.target_format.upper() == img.format.upper():
            try:
                shutil.copyfile(self.__absoluteOriginalFilename(transformation_request.image_id), 
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
    
    

