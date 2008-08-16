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
from twisted.web2.resource import Resource
from twisted.web2 import http
from imgserver.web.twistedweb2.derivedresource import DerivedResource
from imgserver.web.twistedweb2.originalresource import OriginalResource


class TopLevelResource(Resource):
    addSlash = True
    
    def __init__(self, site_config, image_processor):
        self.__site_config = site_config
        self.__image_processor = image_processor
        self.child_original = OriginalResource(site_config, image_processor)
        self.child_derived = DerivedResource(site_config, image_processor)
        
    
    def render(self, ctx):
        return http.Response(stream="Top Level!")