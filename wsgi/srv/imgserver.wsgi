import sys
sys.stdout = sys.stderr

from imgserver.web.site import create_site
import cherrypy
import os
import atexit

imgserver_config = os.path.join(os.path.dirname(__file__), 'imgserver.conf')

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

# quick hack to get the configuration _before_ mounting the application
imgserver_config = cherrypy._cpconfig._Parser().dict_from_file(imgserver_config)

application = cherrypy.Application(create_site(imgserver_config['imgserver']), None)
application.merge(imgserver_config)
   