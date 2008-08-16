"""
    ImgServer RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of ImgServer.

    ImgServer is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ImgServer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with ImgServer.  If not, see <http://www.gnu.org/licenses/>.

"""
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