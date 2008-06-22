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
        assert status is not None
        
        self.id = itemId
        self.status = status
        self.width = size[0] if type(size[0]) == int else int(size[0])
        self.height = size[1] if type(size[1]) == int else int(size[1])
        self.format = format
        
    def getSize(self):
        return (self.width, self.height)

    size = property(getSize, None, None, "Size's Docstring")

class OriginalItem(AbstractItem):
    def __init__(self, itemId, status, size, format):
        assert itemId is not None
        super(OriginalItem, self).__init__(itemId, status, size, format)
        
class DerivedItem(AbstractItem):
    def __init__(self, status, size, format, originalItem):
        assert originalItem is not None
        self.originalItem = originalItem
        
        super(DerivedItem, self).__init__("%s-%sx%s-%s" % (originalItem.id, size[0], size[1], format),status, size, format)