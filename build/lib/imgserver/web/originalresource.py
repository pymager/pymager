import os
import time
import tempfile
from twisted.web2.resource import Resource,PostableResource
from twisted.internet import threads, defer, reactor
from twisted.web2 import http, static, responsecode, stream
from twisted.web2.resource import Resource

FILE_FIELD_NAME = "file"
PERMISSIONS = 0644
TMP_DIR = "fileuploads"

class PostableOriginalResource(PostableResource):
    def __init__(self, site_config, image_processor, item_id):
        super(PostableOriginalResource, self).__init__()
        self.__site_config = site_config
        self.__image_processor = image_processor
        self.__item_id = item_id

    def makeUniqueName(self, filename):
        """Called when a unique filename is needed.
     
        filename is the name of the file as given by the client.
        Returns the fully qualified path of the file to create. The
        file must not yet exist.
        """     
        return tempfile.mktemp(suffix=os.path.splitext(filename)[1])

    def importFile(self, filename, mimetype, fileobject):
        """Does the I/O dirty work after it calls isSafeToWrite to make
        sure it's safe to write this file.
        @param filename: the filename suggested by the client 
        """
        filestream = stream.FileStream(fileobject)
        outname = self.makeUniqueName(filename)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
        fileobject = os.fdopen(os.open(outname, flags, PERMISSIONS), 'wb', 0)
        deferred_file = stream.readIntoFile(filestream, fileobject)
        def done(_):
            def save():
                self.__image_processor.saveFileToRepository(outname, self.__item_id)
                os.remove(outname)
            return threads.deferToThread(save)
        deferred_file.addCallback(done)
        return deferred_file

    def render(self, request):
        finfo = request.files[FILE_FIELD_NAME]
        if finfo:
            d = defer.Deferred()
            def return_response(_):
                reactor.callLater(0, d.callback, http.RedirectResponse('/original/%s' %self.__item_id))
            def return_error(ex):
                reactor.callLater(0, d.errback, ex)
            deferred_file = self.importFile(*finfo[0])
            deferred_file.addCallback(return_response)
            deferred_file.addErrback(return_error)
            return d 
        else:
            return None
        

class OriginalResource(Resource):
    def __init__(self, site_config, image_processor):
        super(OriginalResource, self).__init__()
        self.__site_config = site_config
        self.__image_processor = image_processor
        
    def render(self, ctx):
        return http.Response(stream="Original Resource!")
    
    def locateChild(self, request, segments):
        if segments:
            item_id = segments[0]
            if request.method == 'POST':
                postableResource = PostableOriginalResource(self.__site_config, self.__image_processor, item_id)
                return postableResource, []
            elif request.method == 'GET':
                def get_original_item():
                    """ prepare the transformation synchronously"""
                    relative_path = self.__image_processor.getOriginalImagePath(item_id)
                    path = os.path.join(self.__site_config.data_directory,relative_path)
                    return static.File(path), []
                return threads.deferToThread(get_original_item)
        # revert to default implementation
        return super(OriginalResource,self).locateChild(request, segments)
