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
        self._last_status_change_date = None
        self.set_status(status)
        self._width = size[0] if type(size[0]) == int else int(size[0])
        self._height = size[1] if type(size[1]) == int else int(size[1])
        self._format = format

    def get_last_status_change_date(self):
        return self._last_status_change_date
    def get_id(self):
        return self._id
    def get_status(self):
        return self._status
    def set_status(self, value):
        assert value is not None
        self._last_status_change_date = datetime.utcnow()
        self._status = value
    def get_width(self):
        return self._width
    def get_height(self):
        return self._height
    def get_format(self):
        return self._format        
    def get_size(self):
        return (self.width, self.height)
    
    def associated_image_path(self, path_generator):
        """ @param: path_generator: a imgserver.resources.pathgenerator.PathGenerator object
            @return: a imgserver.resources.path.Path object
        """
        raise NotImplementedError()

    id = property(get_id, None, None, None)
    status = property(get_status, set_status, None, None)
    width = property(get_width, None, None, None)
    height = property(get_height, None, None, None)
    format = property(get_format, None, None, None)
    size = property(get_size, None, None, None)
    last_status_change_date = property(get_last_status_change_date, None, None, None)