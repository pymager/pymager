from twisted.web2.resource import Resource

class OriginalResource(Resource):
    def __init__(self, site_config, image_processor):
        super(OriginalResource, self).__init__()
        self.__site_config = site_config
        self.__image_processor = image_processor
        