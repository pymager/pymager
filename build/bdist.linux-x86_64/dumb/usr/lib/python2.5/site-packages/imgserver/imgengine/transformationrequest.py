from imgserver.imgengine import checkid

class TransformationRequest(object):
    """ Stores the parameters of an image processing request """
    def __init__(self, imageId, size, target_format):
        """ @param size: a (width, height) tuple
        """
        checkid(imageId)
        
        self.imageId = imageId
        self.size = size
        self.targetFormat = target_format