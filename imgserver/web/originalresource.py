import os
from twisted.web2.resource import Resource
from twisted.internet import threads
from twisted.web2 import http, static
from twisted.web2.resource import Resource

class OriginalResource(Resource):
    def __init__(self, site_config, image_processor):
        super(OriginalResource, self).__init__()
        self.__site_config = site_config
        self.__image_processor = image_processor
        
    def render(self, ctx):
        return http.Response(stream="Original Resource!")
    
    def locateChild(self, request, segments):
        if segments:
            try:
                def prepare_transformation():
                    """ prepare the transformation synchronously"""
                    item_id = segments[0]
                    relative_path = self.__image_processor.getOriginalImagePath(item_id)
                    path = os.path.join(self.__site_config.data_directory,relative_path)
                    return static.File(path), []
                return threads.deferToThread(prepare_transformation)
            except AssertionError:
                pass
        # revert to default implementation
        return super(OriginalResource,self).locateChild(request, segments)
