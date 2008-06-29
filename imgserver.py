#!/usr/bin/env python

# requirements: 
# - python2.5
# - python-imaging
# - python-sqlalchemy (+ python-pysqlite2 if using the SQLite backend)
# - python-zopeinterface
# - python-twisted-core
# - python-twisted-web
# - python-twisted-web2
# Not yet:
# - python-openssl
# - python-pmock ?
# - python-configobj?
# - python-pkg-resources?
# - python-setuptools
# - python-distutils-extra
import time
from imgserver.commandline import main
from twisted.web2 import server, http, resource, channel
from twisted.web2 import static, http_headers, responsecode

class Toplevel(resource.Resource):
    addSlash = True
    child_monkey = static.File('/home/samokk/Desktop/dailyBread.iso')
       
    def render(self, ctx):
        print 'sleeping...'
        #time.sleep(10)
        print 'DONE sleeping...'
        return http.Response(
            200,
            {'content-type': http_headers.MimeType('text', 'html')},
            """<html><body>
             <a href="monkey">The source code of twisted.web2.static</a><br>
             <a href="elephant">A defined child</a></body></html>""")

#if __name__ == '__main__':
    
site = server.Site(Toplevel())
    
from twisted.application import service, strports
application = service.Application("imgserver")
s = strports.service('tcp:8000', channel.HTTPFactory(site))
s.setServiceParent(application)

