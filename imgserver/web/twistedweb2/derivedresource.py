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