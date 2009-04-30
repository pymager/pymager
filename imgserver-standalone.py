#!/usr/bin/env python
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
from imgserver import config
from imgserver import web
import cherrypy
import os

cherrypy.config.update(config.parse_config(__file__, config.GLOBAL_CONFIG_FILENAME))
imgserver_config = config.parse_config(__file__, config.IMGSERVER_CONFIG_FILENAME)

application = cherrypy.tree.mount(
    web.create_site(
        imgserver_config['imgserver']), 
        "", 
    imgserver_config)

cherrypy.server.quickstart()
cherrypy.engine.start()

#if hasattr(cherrypy.engine, 'block'):
    # 3.1 syntax
#    print '3.1'
#    cherrypy.engine.start()
#    cherrypy.engine.block()
#else:
    # 3.0 syntax
#    print '3.0'
#    cherrypy.server.quickstart()
#    cherrypy.engine.start()

