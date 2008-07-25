#!/usr/bin/env python

from imgserver.web.site import create_site
from twisted.web2 import server, channel, static 
from twisted.application import service, strports

application = service.Application("imgserver")
s = strports.service('tcp:3000', channel.SCGIFactory(create_site()))
s.setServiceParent(application)