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

from imgserver.bootstrap import ImageServerFactory, ServiceConfiguration
from imgserver.web._toplevelresource import TopLevelResource
import imgserver.config

image_server_factory = None

def _init_imageprocessor(config):
    global image_server_factory
    image_server_factory = ImageServerFactory(config)
    image_request_processor = image_server_factory.create_image_server()
    #image_request_processor = \
    #    f.create_image_server(
    #        site_config.data_directory, 
    #        'postgres://imgserver:funala@localhost/imgserver',
    #        [(100,100), (800,600)], True)
    from pkg_resources import resource_filename
    if config.dev_mode:
        image_request_processor.save_file_to_repository(resource_filename('imgserver.samples', 'sami.jpg'),'sami')
    return image_request_processor

# allowed_sizes=[(100,100), (800,600)]
def create_site(config):
    app_config = ServiceConfiguration(
        data_directory=config['data_directory'] if (config.__contains__('data_directory')) else '/tmp/imgserver', 
        dburi=config['dburi'] if (config.__contains__('dburi')) else 'sqlite:////tmp/db.sqlite', 
        allowed_sizes=config['allowed_sizes'] if (config.__contains__('allowed_sizes')) else None,
        dev_mode= config['dev_mode'] if (config.__contains__('dev_mode')) else False)
    imgserver.config.set_app_config(app_config)
    top_level_resource = TopLevelResource(app_config, _init_imageprocessor(app_config), image_server_factory.image_format_mapper)
    return top_level_resource 