import sys
sys.stdout = sys.stderr

from pymager import config
from pymager.web.site import create_site
import cherrypy
import os
import atexit

cherrypy.config.update(config.parse_config(__file__, config.GLOBAL_CONFIG_FILENAME))

if cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

pymager_config = config.parse_config(__file__, config.PYMAGER_CONFIG_FILENAME)
application = cherrypy.Application(create_site(pymager_config['pymager']), None)
application.merge(pymager_config)
   