import shutil
from imgserver.factory import ImageServerFactory
from pkg_resources import resource_filename

from imgserver.web.twistedweb2.toplevelresource import TopLevelResource  
from twisted.web2 import server

DB_FILENAME='db.sqlite'


class SiteConfig(object):
    def __init__(self, data_directory):
        self.data_directory = data_directory

def init_imageprocessor(site_config):
    shutil.rmtree(site_config.data_directory,True)
    f = ImageServerFactory()
    imageProcessor = \
        f.createImageServer(
            site_config.data_directory, 
            'sqlite:///%s/%s' % ('/tmp', DB_FILENAME),
            [(100,100), (800,600)],True)
    #imageProcessor = \
    #    f.createImageServer(
    #        site_config.data_directory, 
    #        'postgres://imgserver:funala@localhost/imgserver',
    #        [(100,100), (800,600)], True)
    imageProcessor.saveFileToRepository(resource_filename('imgserver.samples', 'sami.jpg'),'sami')
    return imageProcessor

def create_twisted_site():
    site_config = SiteConfig('/tmp/imgserver')
    return server.Site(
        TopLevelResource(
            site_config, 
            init_imageprocessor(site_config)))
 
create_site = create_twisted_site