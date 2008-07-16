#!/usr/bin/env python

# run with :
# - twistd -n -y imgserver.py
# requirements: 
# - python2.5
# - python-imaging
# - python-sqlalchemy (+ python-pysqlite2 if using the SQLite backend + python-psycopg2 if using postgres)
# - python-zopeinterface
# - python-twisted-core
# - python-twisted-web2
# Not yet:
# - python-openssl
# - python-pmock ?
# - python-configobj?
# - python-pkg-resources?
# - python-setuptools
# - python-distutils-extra


# - Setup uses setuptools

#import time

#if __name__ == '__main__':

import os
from twisted.web2 import channel 
from twisted.application import service, strports
from imgserver.web.site import create_site, SiteConfig
#from imgserver.commandline import main

from setuptools import setup, find_packages
print 'yo!', find_packages(exclude=('tests','tests.*'))
# should be able to access http://localhost:8000/derived/sami-100x100.jpg
#main()
application = service.Application("imgserver")
s = strports.service('tcp:8000', channel.HTTPFactory(create_site(SiteConfig('/tmp/imgserver'))))
s.setServiceParent(application)

#s = server.Site(static.File(DIRECTORY))
#reactor.listenTCP(PORT, channel.HTTPFactory(s))
#reactor.run()