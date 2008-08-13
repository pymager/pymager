#!/usr/bin/env python

from imgserver.web.site import create_site
import cherrypy
import os

global_config = os.path.join(os.path.dirname(__file__), 'imgserver-site.conf')
imgserver_config = os.path.join(os.path.dirname(__file__), 'imgserver.conf')

cherrypy.config.update(global_config)
# quick hack to get the configuration _before_ mounting the application
imgserver_config = cherrypy._cpconfig._Parser().dict_from_file(imgserver_config)
application = cherrypy.tree.mount(
    create_site(
        imgserver_config['imgserver']), 
        "/imgserver", 
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
