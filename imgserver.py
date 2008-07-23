#!/usr/bin/env python

from imgserver.web.site import create_site
import cherrypy

# Max request size is 100MB
#cherrypy.server.max_request_body_size = 104857600

# increase server socket timeout to 60s; we are more tolerant of bad
# quality client-server connections (cherrypy's defult is 10s)
#cherrypy.server.socket_timeout = 60

#cherrypy.config.update({'server.socket_port': 8000, 'log.error_file': 'site.log'})

cherrypy.config.update('imgserver-site.conf')
#cherrypy.quickstart(create_site(), '/', 'imgserver-site.conf')
imgserver_app = cherrypy.tree.mount(create_site(), "", 'imgserver-site.conf')
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
