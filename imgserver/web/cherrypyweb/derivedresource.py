import os
from twisted.internet import threads
from twisted.web2 import http, static
from twisted.web2.resource import Resource
from imgserver import domain
from imgserver.imgengine.transformationrequest import TransformationRequest 
from imgserver.web.deriveditemurldecoder import DerivedItemUrlDecoder,UrlDecodingError
from imgserver.imgengine.imagerequestprocessor import ItemDoesNotExistError
import cherrypy
from cherrypy.lib.static import serve_file

class DerivedResource(object):
    
    def __init__(self, site_config, image_processor):
        super(DerivedResource, self).__init__()
        self.__site_config = site_config
        self.__image_processor = image_processor
    
    def _not_found(self, derived_encoded):
        return cherrypy.NotFound('/derived/%s' % (derived_encoded,))
    
    @cherrypy.expose
    def index(self):
        return "Original Resource!"
    
    @cherrypy.expose
    def default(self, derived_encoded):
        try:
            derivedItemUrlDecoder = DerivedItemUrlDecoder(derived_encoded)
        except UrlDecodingError, ex:
            raise self._not_found(derived_encoded)
        else:
            request = TransformationRequest(
                        derivedItemUrlDecoder.itemid, 
                        (derivedItemUrlDecoder.width,derivedItemUrlDecoder.height),
                        domain.IMAGE_FORMAT_JPEG)
            try:
                relative_path = self.__image_processor.prepareTransformation(request)
            except ItemDoesNotExistError, ex:
                raise self._not_found(derived_encoded)
            path = os.path.join(self.__site_config.data_directory,relative_path)
            return serve_file(path)
    
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