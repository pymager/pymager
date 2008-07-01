import logging
import threading
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session,backref #, eagerload
from zope.interface import Interface, implements
from imgserver import domain
from imgserver.domain.abstractitem import AbstractItem
from imgserver.domain.originalitem import OriginalItem
from imgserver.domain.deriveditem import DerivedItem

log = logging.getLogger('persistence.itemrepository')

class DuplicateEntryException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, duplicateId):
        self.__duplicateId = duplicateId
        Exception.__init__(self, 'Duplicated ID: %s' % duplicateId)

    def getDuplicateId(self):
        return self.__duplicateId
    
    duplicateId = property(getDuplicateId, None, None, "The ID that led to the DuplicateEntryException")

class IItemRepository(Interface):
    """ DDD repository for Original and Derived Items """
    def findOriginalItemById(self, item_id):
        """ Find an OriginalItem by its ID """
    
    def findInconsistentOriginalItems(self, maxResults=100):
        """ Find Original Items that are in an inconsistent state """
    
    def findInconsistentDerivedItems(self, maxResults=100):
        """ Find Derived Items that are in an inconsistent state """
    
    def findDerivedItemByOriginalItemIdSizeAndFormat(self, item_id, size, format):
        """ Find Derived Items By :
            - the Original Item ID
            - the size of the Derived Item
            - the format of the Derived Item """
    def create(self, item):
         """ Create a persistent instance of an item
             @raise DuplicateEntryException: when an item with similar characteristics has already been created   
         """
    
    def update(self, item):    
        """ Create a persistent instance, or update an existing item 
            @raise DuplicateEntryException: when an item with similar characteristics has already been created   """
    def delete(self, item):
        pass
    
class ItemRepository(object):
    implements(IItemRepository)
    
    def __init__(self, persistenceProvider):
        self.__persistenceProvider = persistenceProvider
        self.__template = persistenceProvider.session_template()
    
    def findOriginalItemById(self, item_id):
        def callback(session):
            return session.query(OriginalItem)\
                .filter(OriginalItem._id==item_id)\
                .first()
        return self.__template.do_with_session(callback)

    def findInconsistentOriginalItems(self, maxResults=100):
        def callback(session):
            return session.query(OriginalItem)\
                .filter(AbstractItem._status==domain.STATUS_INCONSISTENT)\
                .limit(maxResults).all()
        return self.__template.do_with_session(callback)
    
    def findInconsistentDerivedItems(self, maxResults=100):
        def callback(session):
            return session.query(DerivedItem)\
                .filter(AbstractItem._status==domain.STATUS_INCONSISTENT)\
                .limit(maxResults).all()
        return self.__template.do_with_session(callback)
    
    def findDerivedItemByOriginalItemIdSizeAndFormat(self, item_id, size, format):
        def callback(session):
            o = session.query(DerivedItem)\
                    .filter_by(_width=size[0])\
                    .filter_by(_height=size[1])\
                    .filter_by(_format=format)\
                    .join('_originalItem', aliased=True)\
                    .filter_by(_id=item_id)\
                    .first()
            # FIXME: http://www.sqlalchemy.org/trac/ticket/1082
            (getattr(o, '_originalItem') if hasattr(o, '_originalItem') else (lambda: None))
            return o
        return self.__template.do_with_session(callback)
    
    def create(self, item):
        def callback(session):
            session.save(item)
        try:
            self.__template.do_with_session(callback)
        except sqlalchemy.exceptions.IntegrityError, ex: 
            raise DuplicateEntryException, item.id
    
    def update(self, item):
        def callback(session):
            session.save_or_update(item)
        try:
            self.__template.do_with_session(callback)
        except sqlalchemy.exceptions.IntegrityError: 
            raise DuplicateEntryException, item.id
    
    def delete(self, item):
        def callback(session):
            session.refresh(item)
            session.delete(item)
        self.__template.do_with_session(callback)
