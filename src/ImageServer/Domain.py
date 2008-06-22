from datetime import datetime

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
        
        self._id = itemId
        self._lastStatusChangeDate = None
        self.setStatus(status)
        self._width = size[0] if type(size[0]) == int else int(size[0])
        self._height = size[1] if type(size[1]) == int else int(size[1])
        self._format = format

    def getLastStatusChangeDate(self):
        return self._lastStatusChangeDate
    def getId(self):
        return self._id
    def getStatus(self):
        return self._status
    def setStatus(self, value):
        assert value is not None
        self._lastStatusChangeDate = datetime.utcnow()
        self._status = value
    def getWidth(self):
        return self._width
    def getHeight(self):
        return self._height
    def getFormat(self):
        return self._format        
    def getSize(self):
        return (self.width, self.height)

    id = property(getId, None, None, None)
    status = property(getStatus, setStatus, None, None)
    width = property(getWidth, None, None, None)
    height = property(getHeight, None, None, None)
    format = property(getFormat, None, None, None)
    size = property(getSize, None, None, None)
    lastStatusChangeDate = property(getLastStatusChangeDate, None, None, None)

class OriginalItem(AbstractItem):
    def __init__(self, itemId, status, size, format):
        assert itemId is not None
        super(OriginalItem, self).__init__(itemId, status, size, format)
        
class DerivedItem(AbstractItem):
    def __init__(self, status, size, format, originalItem):
        assert originalItem is not None
        self._originalItem = originalItem
        
        super(DerivedItem, self).__init__("%s-%sx%s-%s" % (originalItem.id, size[0], size[1], format),status, size, format)

    def getOriginalItem(self):
        return self._originalItem
    
    originalItem = property(getOriginalItem, None, None, None)


