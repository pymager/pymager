"""
    ImgServer RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of ImgServer.

    ImgServer is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ImgServer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with ImgServer.  If not, see <http://www.gnu.org/licenses/>.

"""
import shutil

from imgserver.factory import ImageServerFactory, ServiceConfiguration
from imgserver.web.cherrypyweb.toplevelresource import TopLevelResource


def init_imageprocessor(config):    
    f = ImageServerFactory(config)
    imageProcessor = \
        f.create_image_server()
    #imageProcessor = \
    #    f.create_image_server(
    #        site_config.data_directory, 
    #        'postgres://imgserver:funala@localhost/imgserver',
    #        [(100,100), (800,600)], True)
    from pkg_resources import resource_filename
    if config.dev_mode:
        imageProcessor.save_file_to_repository(resource_filename('imgserver.samples', 'sami.jpg'),'sami')
    return imageProcessor

# allowed_sizes=[(100,100), (800,600)]
def create_site(config):
    config = ServiceConfiguration(
        data_directory=config['data_directory'] if (config.__contains__('data_directory')) else '/tmp/imgserver', 
        dburi=config['dburi'] if (config.__contains__('dburi')) else 'sqlite:////tmp/db.sqlite', 
        allowed_sizes=config['allowed_sizes'] if (config.__contains__('allowed_sizes')) else None,
        dev_mode= config['dev_mode'] if (config.__contains__('dev_mode')) else False)
    top_level_resource = \
        TopLevelResource(
            config, 
            init_imageprocessor(config))
    return top_level_resource 