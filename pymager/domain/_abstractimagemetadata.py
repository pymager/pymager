"""
   Copyright 2010 Sami Dalouche

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from datetime import datetime

class AbstractImageMetadata(object):
    def __init__(self, itemId, status, size, format):
        super(AbstractImageMetadata, self).__init__()
        
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
        """ @param: path_generator: a pymager.resources.pathgenerator.PathGenerator object
            @return: a pymager.resources.path.Path object
        """
        raise NotImplementedError()

    id = property(get_id, None, None, None)
    status = property(get_status, set_status, None, None)
    width = property(get_width, None, None, None)
    height = property(get_height, None, None, None)
    format = property(get_format, None, None, None)
    size = property(get_size, None, None, None)
    last_status_change_date = property(get_last_status_change_date, None, None, None)
