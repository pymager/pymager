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

import cherrypy
from pkg_resources import resource_filename
from pymager.web._originalresource import OriginalResource
from pymager.web._derivedresource import DerivedResource
from pymager import config

class TopLevelResource(object):
    _cp_config = {
        'error_page.400': resource_filename('pymager.web.templates', 'error-default.html'),
        'error_page.403': resource_filename('pymager.web.templates', 'error-default.html'),
        'error_page.404': resource_filename('pymager.web.templates', 'error-default.html'),
        'error_page.409': resource_filename('pymager.web.templates', 'error-default.html')
    }
    def __init__(self, app_config, image_processor, image_format_mapper):
        self.__config = app_config
        self.__image_processor = image_processor
        self.original = OriginalResource(app_config, image_processor)
        self.derived = DerivedResource(app_config, image_processor, image_format_mapper)
    
    #@cherrypy.expose
    #def index(self):
    #    return "Top Level"
