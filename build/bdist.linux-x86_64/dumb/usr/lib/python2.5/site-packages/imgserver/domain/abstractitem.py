from datetime import datetime

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