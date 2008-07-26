import sys
sys.stdout = sys.stderr

from imgserver.web.site import create_site
import cherrypy
import os
import atexit

global_config = os.path.join(os.path.dirname(__file__), 'imgserver-site.conf')
imgserver_config = os.path.join(os.path.dirname(__file__), 'imgserver.conf')

cherrypy.config.update(global_config)

if cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

# quick hack to get the configuration _before_ mounting the application
imgserver_config = cherrypy._cpconfig._Parser().dict_from_file(imgserver_config)
application = cherrypy.tree.mount(
    create_site(
        imgserver_config['imgserver']), 
        "", 
    imgserver_config)