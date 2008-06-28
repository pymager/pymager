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

if __name__ == '__main__':
    from twisted.internet import reactor
    
    def printTime( ):
        print "Current time is", time.strftime("%H:%M:%S")
    def stopReactor( ):
        print "Stopping reactor"
        reactor.stop( )

    reactor.callLater(1, printTime)
    reactor.callLater(2, printTime)
    reactor.callLater(3, printTime)
    reactor.callLater(4, printTime)
    reactor.callLater(5, stopReactor)

    print "Running the reactor..."
    reactor.run( )
    print "Reactor stopped."
    #main()
