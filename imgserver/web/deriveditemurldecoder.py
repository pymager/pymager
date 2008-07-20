import re

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
            self.format = match.group(4).upper()
        else:
            raise UrlDecodingError(url_segment)