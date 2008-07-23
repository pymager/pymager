#!/usr/bin/env python

from imgserver.web.site import create_site
import cherrypy

# Max request size is 100MB
cherrypy.server.max_request_body_size = 104857600

# increase server socket timeout to 60s; we are more tolerant of bad
# quality client-server connections (cherrypy's defult is 10s)
cherrypy.server.socket_timeout = 60
    
cherrypy.quickstart(create_site())
