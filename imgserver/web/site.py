import shutil

from twisted.web2 import server
from imgserver.web.toplevelresource import TopLevelResource
from imgserver import domain
from imgserver.factory import ImageServerFactory
from imgserver.imgengine.transformationrequest import TransformationRequest

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
            'sqlite:///%s/%s' % (site_config.data_directory, DB_FILENAME),
            [(100,100), (800,600)])
    imageProcessor.saveFileToRepository('samples/sami.jpg','sami')
    return imageProcessor

def create_site(site_config):
    return server.Site(
        TopLevelResource(
            site_config, 
            init_imageprocessor(site_config)))