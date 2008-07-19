import shutil
import os
from twisted.web2 import server
from imgserver.web.toplevelresource import TopLevelResource
from imgserver import domain
from imgserver.factory import ImageServerFactory
from imgserver.imgengine.transformationrequest import TransformationRequest
from pkg_resources import resource_filename

DB_FILENAME='db.sqlite'
#TMP_DIR = "fileuploads"

class SiteConfig(object):
    def __init__(self, data_directory):
        self.data_directory = data_directory
        #if not os.path.exists(self.tmpdir()):
        #    print os.path.exists(self.tmpdir())
        #    os.makedirs(self.tmpdir())
        #    print self.tmpdir()
        #    print os.path.exists(self.tmpdir())
    
    #def tmpdir(self):
    #    return os.path.join(self.data_directory, TMP_DIR)

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

def create_site():
    site_config = SiteConfig('/tmp/imgserver')
    return server.Site(
        TopLevelResource(
            site_config, 
            init_imageprocessor(site_config)))
