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

import os
import cherrypy
import logging
from pymager import domain
from pymager import imgengine 
from pymager import web
from pymager.web._derivedimagemetadataurldecoder import DerivedImageMetadataUrlDecoder
from pymager.web._derivedimagemetadataurldecoder import UrlDecodingError

from cherrypy.lib.static import serve_file
logger = logging.getLogger("web.derivedresource")
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
        logger.debug("GET %s" % (derived_urisegment,))
        try:
            derivedItemUrlDecoder = DerivedImageMetadataUrlDecoder(self._image_format_mapper, derived_urisegment)
        except UrlDecodingError:
            raise self.__not_found()
        else:
            try:
                request = imgengine.TransformationRequest(
                            self._image_format_mapper,
                            derivedItemUrlDecoder.itemid,
                            (derivedItemUrlDecoder.width, derivedItemUrlDecoder.height),
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
                    raise cherrypy.HTTPError(status=403, message="The requested image transformation is not allowed (%sx%s)" % (derivedItemUrlDecoder.width, derivedItemUrlDecoder.height))
                path = os.path.join(self.__config.data_directory, relative_path)
                return serve_file(path)
