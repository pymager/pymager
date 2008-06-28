from imgserver.domain.abstractitem import AbstractItem

class OriginalItem(AbstractItem):
    def __init__(self, itemId, status, size, format):
        assert itemId is not None
        super(OriginalItem, self).__init__(itemId, status, size, format)