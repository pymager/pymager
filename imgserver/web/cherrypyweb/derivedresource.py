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
import os
from imgserver import domain
from imgserver.imgengine.transformationrequest import TransformationRequest 
from imgserver.web.deriveditemurldecoder import DerivedItemUrlDecoder,UrlDecodingError
from imgserver.imgengine.imagerequestprocessor import ItemDoesNotExistError
import cherrypy
from cherrypy.lib.static import serve_file

class DerivedResource(object):
    def __init__(self, config, image_processor):
        super(DerivedResource, self).__init__()
        self.__config = config
        self.__image_processor = image_processor
    
    def __not_found(self):
        return cherrypy.NotFound(cherrypy.request.path_info)
    
    @cherrypy.expose
    def index(self):
        return "Original Resource!"
    
    @cherrypy.expose
    def default(self, derived_urisegment):
        try:
            derivedItemUrlDecoder = DerivedItemUrlDecoder(derived_urisegment)
        except UrlDecodingError:
            raise self.__not_found()
        else:
            request = TransformationRequest(
                        derivedItemUrlDecoder.itemid, 
                        (derivedItemUrlDecoder.width,derivedItemUrlDecoder.height),
                        derivedItemUrlDecoder.format)
            try:
                relative_path = self.__image_processor.prepareTransformation(request)
            except ItemDoesNotExistError:
                raise self.__not_found()
            path = os.path.join(self.__config.data_directory,relative_path)
            return serve_file(path)