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