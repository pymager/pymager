import sys
sys.stdout = sys.stderr

from pymager import config
from pymager import web 
import cherrypy
import os
import atexit

cherrypy.config.update(config.parse_config(__file__, config.GLOBAL_CONFIG_FILENAME))
pymager_config = config.parse_config(__file__, config.PYMAGER_CONFIG_FILENAME)
application = cherrypy.Application(web.create_site(pymager_config['pymager']), None)
application.merge(pymager_config)
