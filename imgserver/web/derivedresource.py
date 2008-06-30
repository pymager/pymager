import re
import os
from twisted.web2 import http, static
from twisted.web2.resource import Resource

# itemId-800x600.jpg
FILENAME_REGEX = re.compile(r'([a-zA-Z\d]+)\-(\d+)x(\d+)\.([a-zA-Z]+)')

class UrlDecodingError(Exception):
    def __init__(self, url_segment):
        self.url_segment = url_segment

class DerivedItemUrlDecoder(object):
    def __init__(self, url_segment):
        super(DerivedItemUrlDecoder, self).__init__()
        match = FILENAME_REGEX.match(url_segment)
        if match and len(match.groups()) == 4:
            self.itemid = match.group(1)
            self.width = int(match.group(2))
            self.height = int(match.group(3))
            self.ext = match.group(4)
        else:
            raise UrlDecodingError(url_segment)

class DerivedResource(Resource):
    
    def __init__(self, site_config):
        super(DerivedResource, self).__init__()
        self.__site_config = site_config
    
    def render(self, ctx):
        return http.Response(stream="Derived Resource!")
    
    def locateChild(self, request, segments):
        if segments:
            try:
                derivedItemUrlDecoder = DerivedItemUrlDecoder(segments[0])
                path = os.path.join(self.__site_config.data_directory, 'cache', '%s-%sx%s.%s' % (
                    derivedItemUrlDecoder.itemid, 
                    derivedItemUrlDecoder.width, 
                    derivedItemUrlDecoder.height, 
                    derivedItemUrlDecoder.ext))
                print path
                return static.File(path), []
            except AssertionError:
                pass
                
        #child, segment = Resource.locateChild(request, segments)
        return super(DerivedResource,self).locateChild(request, segments)
        