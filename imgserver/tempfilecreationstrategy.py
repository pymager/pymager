from zope.interface import Interface, implements
import tempfile
import os
import sys

def createTempFileStrategy():
    """ Returns an instance of ITempFileCreationStrategy
    that is suitable for the current system"""
    
    if sys.platform == 'win32':
        return ITempFileCreationStrategy(WindowsFileCreationStrategy())
    else:
        return ITempFileCreationStrategy(UnixTempFileCreationStrategy())

class ITempFileCreationStrategy(Interface):
    """ Strategy to create and delete 
    temporary files """
    
    def createTempFile(self):
        """ returns an OS-level handle 
        to an open file (as would be 
        returned by os.open()) """
    
    def deleteTempFile(self, file):
        """ deletes the file corresponding to a temp file"""

class UnixTempFileCreationStrategy(object):
    implements(ITempFileCreationStrategy)
    def createTempFile(self):
        return tempfile.NamedTemporaryFile()
    
    def deleteTempFile(self, file):
        # do nothing
        pass

class WindowsFileCreationStrategy(object):
    implements(ITempFileCreationStrategy)
    def createTempFile(self):
        return tempfile.mkstemp()
    
    def deleteTempFile(self, file):
        os.remove(file.filename)