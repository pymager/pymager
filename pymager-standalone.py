#!/usr/bin/env python
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
from pymager import config
from pymager import web
import cherrypy
import os

if __name__ == '__main__':
    cherrypy.config.update(config.parse_config(__file__, config.GLOBAL_CONFIG_FILENAME))
    pymager_config = config.parse_config(__file__, config.PYMAGER_CONFIG_FILENAME)

    application = cherrypy.tree.mount(
          web.create_site(pymager_config['pymager']),
          "",
          pymager_config)

    cherrypy.engine.start()
    cherrypy.engine.block()