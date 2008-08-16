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
from imgserver.web.cherrypyweb.originalresource import OriginalResource
from imgserver.web.cherrypyweb.derivedresource import DerivedResource
from twisted.web2.resource import Resource
from twisted.web2 import http
import cherrypy

class TopLevelResource(object):
    def __init__(self, config, image_processor):
        self.__config = config
        self.__image_processor = image_processor
        self.original = OriginalResource(config, image_processor)
        self.derived = DerivedResource(config, image_processor)
    
    @cherrypy.expose
    def index(self):
        return "Top Level"