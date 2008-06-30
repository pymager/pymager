from twisted.web2.resource import Resource

class OriginalResource(Resource):
    def __init__(self, site_config):
        super(OriginalResource, self).__init__()
        self.__site_config = site_config
        