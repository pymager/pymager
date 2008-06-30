from twisted.web2.resource import Resource
from twisted.web2 import http
from imgserver.web.derivedresource import DerivedResource
from imgserver.web.originalresource import OriginalResource


class TopLevelResource(Resource):
    addSlash = True
    
    def __init__(self, site_config):
        self.__site_config = site_config
        self.child_original = OriginalResource(site_config)
        self.child_derived = DerivedResource(site_config)
    
    def render(self, ctx):
        return http.Response(stream="Top Level!")