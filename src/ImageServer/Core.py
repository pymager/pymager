import Image, ImageOps
import mimetypes
import os, os.path

# Relative to the data_directory
CacheDirectory = "cache"
OriginalDirectory = "original"

# Layout
# data/original/image_id.format
# data/cache/image_id/800x600/format


class ImageProcessingException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class ImageRequest():
    def __init__(self, image_id, size, target_format):
        """ @param size: a (width, height) tuple
        """
        self.image_id = image_id
        self.size = size
        self.target_format = target_format

class ImageRequestProcessor():
    def __init__(self, data_directory):
        self.data_directory = data_directory
        
        # initialize directories
        for dir in [self.cache_directory(), self.original_directory()]:
            if not os.path.exists(dir):
                os.makedirs(dir)

    def cache_directory(self):
        return '%s/%s' % (self.data_directory, CacheDirectory)
    
    def original_directory(self):
        return '%s/%s' % (self.data_directory, OriginalDirectory)
    
    def prepare_request(self, image_request):
        """ Takes an ImageRequest and prepare the output for it.
            @return: nothing for now... The prepared image will be available in data_directory/cache"""
        img = Image.open('../samples/%s.jpg' % image_request.image_id)
        target_image = ImageOps.fit(image=img, size=image_request.size, centering=(0.5,0.5))
        try:
            target_image.save('%s/%s-%sx%s.%s' % (  self.cache_directory(),
                                                     image_request.image_id, 
                                                     image_request.size[0], 
                                                     image_request.size[1], 
                                                     image_request.target_format))
        except IOError, e:
            raise ImageProcessingException, e

