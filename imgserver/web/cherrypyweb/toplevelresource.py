from imgserver.web.cherrypyweb.originalresource import OriginalResource
from twisted.web2.resource import Resource
from twisted.web2 import http
import cherrypy

class TopLevelResource(object):
    def __init__(self, site_config, image_processor):
        self.__site_config = site_config
        self.__image_processor = image_processor
        self.original = OriginalResource(site_config, image_processor)
        #self.derived = DerivedResource(site_config, image_processor)
    
    @cherrypy.expose
    def index(self):
        return "Top Level"