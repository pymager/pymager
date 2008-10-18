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
import os
import cgi
import time
import tempfile
import cherrypy
from cherrypy.lib.static import serve_file
from imgserver.imgengine.imagerequestprocessor import ItemDoesNotExistError

FILE_FIELD_NAME = "file"
PERMISSIONS = 0644
TMP_DIR = "fileuploads"

def noBodyProcess():
    """Sets cherrypy.request.process_request_body = False, giving
    us direct control of the file upload destination. By default
    cherrypy loads it to memory, we are directing it to disk."""
    if cherrypy.request.method == 'POST':
        cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)

class OriginalResource(object):
    def __init__(self, config, image_processor):
        super(OriginalResource, self).__init__()
        self.__config = config
        self.__image_processor = image_processor
        
    @cherrypy.expose
    def index(self):
        return "Original Resource!"
    
    @cherrypy.expose
    @cherrypy.tools.noBodyProcess()
    def default(self, *args, **kwargs):
        dispatch_method_name = 'default_%s' %(cherrypy.request.method) 
        return (getattr(self, dispatch_method_name) if hasattr(self, dispatch_method_name) else (lambda: None))(*args, **kwargs)  
    
    # http://tools.cherrypy.org/wiki/DirectToDiskFileUpload
    # @cherrypy.expose
    def default_GET(self, item_id):
        try:
            relative_path = self.__image_processor.getOriginalImagePath(item_id)
        except ItemDoesNotExistError:
            raise cherrypy.NotFound(cherrypy.request.path_info)
        else:
            path = os.path.join(self.__config.data_directory,relative_path)
            return serve_file(path)
    
    def default_POST(self, item_id):
        """ See http://tools.cherrypy.org/wiki/DirectToDiskFileUpload 
        """
        cherrypy.response.timeout = 3600
    
        # convert the header keys to lower case
        lcHDRS = {}
        for key, val in cherrypy.request.headers.iteritems():
            lcHDRS[key.lower()] = val

        # at this point we could limit the upload on content-length...
        # incomingBytes = int(lcHDRS['content-length'])
        
        # create our version of cgi.FieldStorage to parse the MIME encoded
        # form data where the file is contained
        formFields = cgi.FieldStorage(fp=cherrypy.request.rfile,
            headers=lcHDRS,
            environ={'REQUEST_METHOD':'POST'},
            keep_blank_values=True)

        theFile = formFields[FILE_FIELD_NAME]
        self.__image_processor.saveFileToRepository(theFile.file, item_id)
        
        #myFieldStorage.strategy.deleteTempFile(theFile)
        raise cherrypy.HTTPRedirect('%s%s' % (cherrypy.request.script_name, cherrypy.request.path_info)) 
        