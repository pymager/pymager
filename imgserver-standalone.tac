#!/usr/bin/env python

# run with :
# - twistd -n -y imgserver.py
#
# http://localhost:8000/derived/sami-100x100.jpg
# http://localhost:8000/derived/sami-800x600.jpg

from imgserver.web.site import create_site
from twisted.web2 import channel 
from twisted.application import service, strports

application = service.Application("imgserver")
s = strports.service('tcp:8000', channel.HTTPFactory(create_site()))
s.setServiceParent(application)