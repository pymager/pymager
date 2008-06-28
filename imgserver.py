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
from imgserver.web import protocol

if __name__ == '__main__':
    from twisted.internet import reactor
    
    def stopReactor( ):
        print "Stopping reactor"
        reactor.stop( )

    #reactor.callLater(5, stopReactor)
    reactor.listenTCP(8000, protocol.MyHttpFactory( ))
    
    print "Running the reactor..."
    reactor.run( )
    print "Reactor stopped."
    
    
