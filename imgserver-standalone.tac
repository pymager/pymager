#!/usr/bin/env python

# run with :
# - twistd -n -y imgserver.py
#
# http://localhost:8000/derived/sami-100x100.jpg
# http://localhost:8000/derived/sami-800x600.jpg
# requirements: 
# - python2.5
# - python-imaging
# - python-sqlalchemy (+ python-pysqlite2 if using the SQLite backend + python-psycopg2 if using postgres)
# - python-zopeinterface
# - python-twisted-core
# - python-twisted-web2
# - python-pkg-resources?
# - python-setuptools
# Not yet:
# - python-pmock ?
# - python-configobj?
# - python-distutils-extra

#import time

#if __name__ == '__main__':
import os
from imgserver.web.site import create_site, SiteConfig
from twisted.web2 import channel 
from twisted.application import service, strports

application = service.Application("imgserver")
s = strports.service('tcp:8000', channel.HTTPFactory(create_site()))
s.setServiceParent(application)