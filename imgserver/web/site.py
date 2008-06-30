from twisted.web2 import server
from imgserver.web.toplevelresource import TopLevelResource

class SiteConfig(object):
    def __init__(self, data_directory):
        self.data_directory = data_directory

def create_site(site_config):
    return server.Site(TopLevelResource(site_config))