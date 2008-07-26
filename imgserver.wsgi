#!/usr/bin/env python

from imgserver.web.site import create_site
import cherrypy

global_config = 'imgserver-site.conf'
imgserver_config = 'imgserver.conf'

cherrypy.config.update(global_config)

# quick hack to get the configuration _before_ mounting the application
imgserver_config = cherrypy._cpconfig._Parser().dict_from_file(imgserver_config)
application = cherrypy.tree.mount(
    create_site(
        imgserver_config['imgserver']), 
        "", 
    imgserver_config)