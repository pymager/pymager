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
from twisted.internet import threads
from twisted.web2 import http, static
from twisted.web2.resource import Resource
from imgserver import domain
from imgserver.imgengine.transformationrequest import TransformationRequest 
from imgserver.web.deriveditemurldecoder import DerivedItemUrlDecoder,UrlDecodingError

class DerivedResource(Resource):
    
    def __init__(self, site_config, image_processor):
        super(DerivedResource, self).__init__()
        self.__site_config = site_config
        self.__image_processor = image_processor
    
    def render(self, ctx):
        return http.Response(stream="Derived Resource!")
    
    def locateChild(self, request, segments):
        if segments:
            try:
                def prepare_transformation():
                    """ prepare the transformation synchronously"""
                    derivedItemUrlDecoder = DerivedItemUrlDecoder(segments[0])
                    request = TransformationRequest(
                        derivedItemUrlDecoder.itemid, 
                        (derivedItemUrlDecoder.width,derivedItemUrlDecoder.height),
                        domain.IMAGE_FORMAT_JPEG)
                    relative_path = self.__image_processor.prepareTransformation(request)
                    path = os.path.join(self.__site_config.data_directory,relative_path)
                    return static.File(path), []
                return threads.deferToThread(prepare_transformation)
            except AssertionError:
                pass
        # revert to default implementation
        return super(DerivedResource,self).locateChild(request, segments)