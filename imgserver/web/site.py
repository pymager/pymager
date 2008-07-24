import shutil

from imgserver.factory import ImageServerFactory, ServiceConfiguration
from imgserver.web.cherrypyweb.toplevelresource import TopLevelResource

DB_FILENAME='db.sqlite'

def init_imageprocessor(config):    
    f = ImageServerFactory(config)
    imageProcessor = \
        f.createImageServer()
    #imageProcessor = \
    #    f.createImageServer(
    #        site_config.data_directory, 
    #        'postgres://imgserver:funala@localhost/imgserver',
    #        [(100,100), (800,600)], True)
    from pkg_resources import resource_filename
    imageProcessor.saveFileToRepository(resource_filename('imgserver.samples', 'sami.jpg'),'sami')
    return imageProcessor

def create_site():
    config = ServiceConfiguration('/tmp/imgserver', 
        dburi='sqlite:////tmp/db.sqlite', 
        allowed_sizes=[(100,100), (800,600)], 
        drop_data=True)
    top_level_resource = \
        TopLevelResource(
            config, 
            init_imageprocessor(config))
    return top_level_resource 