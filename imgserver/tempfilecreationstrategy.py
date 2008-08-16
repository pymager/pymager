"""
    ImgServer RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of ImgServer.

    ImgServer is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ImgServer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with ImgServer.  If not, see <http://www.gnu.org/licenses/>.

"""
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