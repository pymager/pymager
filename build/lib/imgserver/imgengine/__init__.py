class ImageProcessingException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, message):
        super(ImageProcessingException, self).__init__(message)
        
class IDNotAuthorized(ImageProcessingException):
    def __init__(self, imageId):
        super(IDNotAuthorized, self).__init__('ID contains non alpha numeric characters: %s' % (imageId,))
        self.imageId = imageId

class ImageFileNotRecognized(ImageProcessingException):
    def __init__(self, ex):
        super(ImageFileNotRecognized, self).__init__(ex)

class ImageIDAlreadyExistingException(ImageProcessingException):
    def __init__(self, imageId):
        super(ImageIDAlreadyExistingException, self).__init__('An image with the given ID already exists in the repository: %s' % imageId)
        self.imageId = imageId
        
def checkid(imageId):
    if not imageId.isalnum():
        raise IDNotAuthorized(imageId)