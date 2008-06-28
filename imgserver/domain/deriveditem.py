from imgserver.domain.abstractitem import AbstractItem 

class DerivedItem(AbstractItem):
    def __init__(self, status, size, format, originalItem):
        assert originalItem is not None
        self._originalItem = originalItem
        
        super(DerivedItem, self).__init__("%s-%sx%s-%s" % (originalItem.id, size[0], size[1], format),status, size, format)

    def getOriginalItem(self):
        return self._originalItem
    
    originalItem = property(getOriginalItem, None, None, None)