class AbstractItem():
    def __init__(self, id, status, width, height, format):
        self.__id = id
        self.__status = status
        self.__width = width
        self.__height = height
        self.__format = format
    
    def get_status(self):
        return self.__status
    
    def get_width(self):
        return self.__width
    
    def get_height(self):
        return self.__height
    
    def get_format(self):
        return self.__format

class OriginalItem(AbstractItem):
    def __init__(self, id, status, width, height, format):
        AbstractItem.__init__(self, id, status, width, height, format)
        
class DerivedItem(AbstractItem):
    def __init__(self, id, status, width, height, format, original_item):
        AbstractItem.__init__(self, id, status, width, height, format)
        self.__original_item = original_item
    
    def get_original_item(self):
        return self.__original_item