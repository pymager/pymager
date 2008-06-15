# The possible statuses of a domain object
STATUS_INCONSISTENT = 'INCONSISTENT'
STATUS_OK = 'OK'

IMAGE_FORMAT_JPEG = 'JPEG'

class AbstractItem(object):
    def __init__(self, itemId, status, size, format):
        super(AbstractItem, self).__init__()
        
        assert size is not None
        assert len(size) == 2
        assert size[0] is not None
        assert size[1] is not None
        assert format is not None
        
        self.__id = itemId
        self.setStatus(status)
        self.__width = size[0] if type(size[0]) == int else int(size[0])
        self.__height = size[1] if type(size[1]) == int else int(size[1])
        self.__format = format

    def getStatus(self):
        return self.__status

    def setStatus(self, value):
        assert value is not None
        self.__status = value

    def getId(self):
        return self.__id

    def getWidth(self):
        return self.__width

    def getHeight(self):
        return self.__height


    def getFormat(self):
        return self.__format
    
    def getSize(self):
        return (self.__width, self.__height)
    
    id = property(getId, None, None, "Id's Docstring")
    status = property(getStatus, setStatus, None, "Status's Docstring")
    width = property(getWidth, None, None, "Width's Docstring")
    height = property(getHeight, None, None, "Height's Docstring")
    format = property(getFormat, None, None, "Format's Docstring")
    size = property(getSize, None, None, "Size's Docstring")

class OriginalItem(AbstractItem):
    def __init__(self, itemId, status, size, format):
        assert itemId is not None
        super(OriginalItem, self).__init__(itemId, status, size, format)
        
class DerivedItem(AbstractItem):
    def __init__(self, status, size, format, originalItem):
        assert originalItem is not None
        self.__originalItem = originalItem
        
        super(DerivedItem, self).__init__("%s-%sx%s-%s" % (originalItem.id, size[0], size[1], format),status, size, format)
        

    def getOriginalItem(self):
        return self.__originalItem
    
    originalItem = property(getOriginalItem, None, None, "OriginalItem's Docstring")