# See http://www.sqlalchemy.org/trac/ticket/1082

import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session, eagerload
from sqlalchemy.sql import select

import os

STATUS_INCONSISTENT = 'INCONSISTENT'
STATUS_OK = 'OK'

IMAGE_FORMAT_JPEG = 'JPEG'

class AbstractItem(object):
    def __init__(self, itemId, status, size, format):
        super(AbstractItem, self).__init__()
        
        self.id = itemId
        self.status = status
        self.width = size[0] if type(size[0]) == int else int(size[0])
        self.height = size[1] if type(size[1]) == int else int(size[1])
        self.format = format

class OriginalItem(AbstractItem):
    def __init__(self, itemId, status, size, format):
        assert itemId is not None
        super(OriginalItem, self).__init__(itemId, status, size, format)
        
class DerivedItem(AbstractItem):
    def __init__(self, status, size, format, originalItem):
        self.originalItem = originalItem
        super(DerivedItem, self).__init__("%s-%sx%s-%s" % (originalItem.id, size[0], size[1], format),status, size, format)
        
engine = create_engine('sqlite:///:memory:', encoding='utf-8', echo=False)
metadata = MetaData()
sm = sessionmaker(bind=engine, autoflush=True, transactional=True)
        
abstract_item = Table('abstract_item', metadata,
    Column('id', String(255), primary_key=True),
    Column('status', String(255), index=True, nullable=False),
    Column('width', Integer, index=True, nullable=False),
    Column('height', Integer, index=True, nullable=False),
    Column('format', String(255), index=True, nullable=False),
    Column('type', String(255), nullable=False)
)
        
original_item = Table('original_item', metadata,
    Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True),
)
        
derived_item = Table('derived_item', metadata,
    Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True),
    Column('original_item_id', String(255), ForeignKey('original_item.id', ondelete="CASCADE"))
)

mapper(AbstractItem, abstract_item, polymorphic_on=abstract_item.c.type, polymorphic_identity='ABSTRACT_ITEM') 
mapper(OriginalItem, original_item, inherits=AbstractItem, polymorphic_identity='ORIGINAL_ITEM')
mapper(DerivedItem, derived_item, 
       properties={ 
                   'originalItem' : relation(OriginalItem, primaryjoin=derived_item.c.original_item_id==original_item.c.id)
                   }, inherits=AbstractItem , polymorphic_identity='DERIVED_ITEM')

metadata.create_all(engine)

session = sm()
originalItem = OriginalItem('MYID12435', STATUS_OK, (800, 600), IMAGE_FORMAT_JPEG)
session.save(originalItem)
session.commit()
session.close()

session = sm()
item = DerivedItem(STATUS_OK, (100, 100), IMAGE_FORMAT_JPEG, originalItem)
session.save(item)
session.commit()
session.close()

session = sm()
foundItem = session.query(DerivedItem)\
    .filter_by(width=100)\
    .filter_by(height=100)\
    .filter_by(format=IMAGE_FORMAT_JPEG)\
    .join('originalItem', aliased=True)\
    .filter_by(id='MYID12435')\
    .first()

assert foundItem is not None
assert foundItem.status == STATUS_OK
assert foundItem.width == 100
assert foundItem.height == 100
assert foundItem.format == IMAGE_FORMAT_JPEG
assert foundItem.originalItem.id == 'MYID12435'
assert foundItem.originalItem.status == STATUS_OK
assert foundItem.originalItem.width == 800
assert foundItem.originalItem.height == 600
assert foundItem.originalItem.format == IMAGE_FORMAT_JPEG
        
session.commit()
session.close() 