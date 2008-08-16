import sys
sys.stdout = sys.stderr

from imgserver import config
from imgserver.web.site import create_site
import cherrypy
import os
import atexit

cherrypy.config.update(config.parse_config(__file__, config.GLOBAL_CONFIG_FILENAME))

if cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

imgserver_config = config.parse_config(__file__, config.IMGSERVER_CONFIG_FILENAME)
application = cherrypy.Application(create_site(imgserver_config['imgserver']), None)
application.merge(imgserver_config)
   