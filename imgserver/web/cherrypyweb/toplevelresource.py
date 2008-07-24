from imgserver.web.cherrypyweb.originalresource import OriginalResource
from imgserver.web.cherrypyweb.derivedresource import DerivedResource
from twisted.web2.resource import Resource
from twisted.web2 import http
import cherrypy

class TopLevelResource(object):
    def __init__(self, config, image_processor):
        self.__config = config
        self.__image_processor = image_processor
        self.original = OriginalResource(config, image_processor)
        self.derived = DerivedResource(config, image_processor)
    
    @cherrypy.expose
    def index(self):
        return "Top Level"