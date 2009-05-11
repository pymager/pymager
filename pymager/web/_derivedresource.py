"""
    PyMager RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of PyMager.

    PyMager is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyMager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with PyMager.  If not, see <http://www.gnu.org/licenses/>.

"""
import os
import cherrypy
from pymager import domain
from pymager import imgengine 
from pymager import web
from pymager.web._derivedimagemetadataurldecoder import DerivedImageMetadataUrlDecoder
from pymager.web._derivedimagemetadataurldecoder import UrlDecodingError

from cherrypy.lib.static import serve_file

class DerivedResource(object):
    exposed = True

    def __init__(self, config, image_processor, image_format_mapper):
        super(DerivedResource, self).__init__()
        self.__config = config
        self.__image_processor = image_processor
        self._image_format_mapper = image_format_mapper
    
    def __not_found(self):
        return cherrypy.NotFound(cherrypy.request.path_info)
    
    #@cherrypy.expose
    #def index(self):
    #    return "Derived Resource!"
    
    #@cherrypy.expose
    def GET(self, derived_urisegment):
        try:
            derivedItemUrlDecoder = DerivedImageMetadataUrlDecoder(self._image_format_mapper, derived_urisegment)
        except UrlDecodingError:
            raise self.__not_found()
        else:
            try:
                request = imgengine.TransformationRequest(
                            self._image_format_mapper,
                            derivedItemUrlDecoder.itemid, 
                            (derivedItemUrlDecoder.width,derivedItemUrlDecoder.height),
                            derivedItemUrlDecoder.format)
            except imgengine.ImageFormatNotSupportedException, e:
                print e.image_format
                raise cherrypy.HTTPError(status=400, message="The requested image format is Invalid: %s" % (e.image_format))
            else:
                try:
                    relative_path = self.__image_processor.prepare_transformation(request)
                except imgengine.ImageMetadataNotFoundException:
                    raise self.__not_found()
                except imgengine.SecurityCheckException:
                    raise cherrypy.HTTPError(status=403, message="The requested image transformation is not allowed (%sx%s)" % (derivedItemUrlDecoder.width,derivedItemUrlDecoder.height))
                path = os.path.join(self.__config.data_directory,relative_path)
                return serve_file(path)