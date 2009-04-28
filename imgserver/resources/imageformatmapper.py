from zope.interface import Interface, implements

class ImageFormatMapper(Interface):
    def supports_format(self, format):
        """ @return:  a boolean indicating whether the given format is supported """
    
    def supports_extension(self, extension):
        """ @return: a boolean indicating if whether the given format is supported"""
    
    def extension_to_format(self, extension):
        """ converts an extension (string) to a standardized format name (string)"""
    
    def format_to_extension(self, format):
        """ converts a format (string) to an extension (string)"""