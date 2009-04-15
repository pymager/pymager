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
from imgserver.domain.abstractitem import AbstractItem 

class DerivedItem(AbstractItem):
    def __init__(self, status, size, format, original_item):
        assert original_item is not None
        self._original_item = original_item
        
        super(DerivedItem, self).__init__("%s-%sx%s-%s" % (original_item.id, size[0], size[1], format),status, size, format)

    def get_original_item(self):
        return self._original_item
    
    def associated_image_path(self, path_generator):
        return path_generator.derived_path(self)
    
    original_item = property(get_original_item, None, None, None)