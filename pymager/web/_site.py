"""
   Copyright 2010 Sami Dalouche

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import shutil

from pymager.bootstrap import ImageServerFactory, ServiceConfiguration
from pymager.web._toplevelresource import TopLevelResource
import pymager.config

image_server_factory = None

def _init_imageprocessor(config):
    global image_server_factory
    image_server_factory = ImageServerFactory(config)
    image_request_processor = image_server_factory.create_image_server()
    from pkg_resources import resource_filename
    return image_request_processor

# allowed_sizes=[(100,100), (800,600)]
def create_site(config):
    app_config = ServiceConfiguration(
        data_directory=config['data_directory'] if (config.__contains__('data_directory')) else '/tmp/pymager',
        dburi=config['dburi'] if (config.__contains__('dburi')) else 'sqlite:////tmp/db.sqlite',
        allowed_sizes=config['allowed_sizes'] if (config.__contains__('allowed_sizes')) else None,
        dev_mode=config['dev_mode'] if (config.__contains__('dev_mode')) else False)
    pymager.config.set_app_config(app_config)
    top_level_resource = TopLevelResource(app_config, _init_imageprocessor(app_config), image_server_factory.image_format_mapper)
    return top_level_resource 
