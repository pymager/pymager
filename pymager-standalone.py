#!/usr/bin/env python
"""
    PyMager RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of PyMager.

    PyMager is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyMager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with PyMager.  If not, see <http://www.gnu.org/licenses/>.

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