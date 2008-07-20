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