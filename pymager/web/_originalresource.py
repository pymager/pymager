"""
   Copyright 2010 Sami Dalouche

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
import cgi
import time
import tempfile
import hashlib
import cherrypy
import logging
from cherrypy.lib.static import serve_file
from pymager import config
from pymager import imgengine

FILE_FIELD_NAME = "file"
PERMISSIONS = 0644
TMP_DIR = "fileuploads"
BASIC_AUTH_REALM = "Image Server"
logger = logging.getLogger("web.originalresource")

def disable_body_processing():
    """Sets cherrypy.request.process_request_body = False, giving
    us direct control of the file upload destination. By default
    cherrypy loads it to memory, we are directing it to disk."""
    if cherrypy.request.method in ('POST', 'PUT'):
        cherrypy.request.process_request_body = False

def enable_basic_auth():
    """Enables basic authentication when we are running in the dev_mode. (should be handled by Apache in production)"""
    def fetch_users():
        def md5pass(password):
            m = hashlib.md5()
            m.update(password)
            return m.hexdigest()
        return {'test': md5pass('test')}
    #if config.app_config().dev_mode:
    if cherrypy.request.method in ('POST', 'DELETE', 'PUT') and config.app_config().dev_mode:
        cherrypy.tools.basic_auth.callable(realm=BASIC_AUTH_REALM, users=fetch_users)

cherrypy.tools.disable_body_processing = cherrypy.Tool('before_request_body', disable_body_processing)
cherrypy.tools.enable_basic_auth = cherrypy.Tool('before_request_body', enable_basic_auth)

class OriginalResource(object):
    exposed = True
    _cp_config = {
        'tools.disable_body_processing.on' : True,
        'tools.enable_basic_auth.on' : True
    }
    def __init__(self, app_config, image_processor):
        super(OriginalResource, self).__init__()
        self.__app_config = app_config
        self.__image_processor = image_processor
        
    #@cherrypy.expose
    #def index(self):
    #    return "Original Resource!"
    
    #@cherrypy.expose
    #@cherrypy.tools.enable_basic_auth()
    #@cherrypy.tools.disable_body_processing()
    #def default(self, *args, **kwargs):
    #    dispatch_method_name = 'default_%s' %(cherrypy.request.method) 
    #    return (getattr(self, dispatch_method_name) if hasattr(self, dispatch_method_name) else (lambda: None))(*args, **kwargs)  
   
    # http://tools.cherrypy.org/wiki/DirectToDiskFileUpload
    # @cherrypy.expose
    def GET(self, image_id):
        logger.debug("GET %s" % (image_id,))
        try:
            relative_path = self.__image_processor.get_original_image_path(image_id)
        except imgengine.ImageMetadataNotFoundException:
            raise cherrypy.NotFound(cherrypy.request.path_info)
        else:
            path = os.path.join(self.__app_config.data_directory, relative_path)
            return serve_file(path)
    
    #@cherrypy.tools.enable_basic_auth()
    #@cherrypy.tools.disable_body_processing()
    def DELETE(self, image_id):
        logger.debug("DELETE %s" % (image_id,))
        try:
            self.__image_processor.delete(image_id)
        except imgengine.ImageMetadataNotFoundException:
            raise cherrypy.NotFound(cherrypy.request.path_info)
        
    #@cherrypy.tools.enable_basic_auth()
    #@cherrypy.tools.disable_body_processing()
    def POST(self, image_id):
        """ See http://tools.cherrypy.org/wiki/DirectToDiskFileUpload 
        """
        logger.debug("POST %s" % (image_id,))
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
        
        if FILE_FIELD_NAME not in formFields:
            raise cherrypy.HTTPError(status=400, message="Multipart Request does not contain a 'file' parameter")
        
        theFile = formFields[FILE_FIELD_NAME]  
            
        try:
            self.__image_processor.save_file_to_repository(theFile.file, image_id)
        except imgengine.ImageIDAlreadyExistsException:
            raise cherrypy.HTTPError(status=409, message="Image ID Already Exists")
        except imgengine.ImageStreamNotRecognizedException:
            raise cherrypy.HTTPError(status=400, message="Unknown Image Format")
        except imgengine.IllegalImageIdException:
            raise cherrypy.HTTPError(status=400, message="Image ID is invalid")
        else:
            #myFieldStorage.strategy.deleteTempFile(theFile)
            raise cherrypy.HTTPRedirect('%s%s' % (cherrypy.request.script_name, cherrypy.request.path_info)) 
        
