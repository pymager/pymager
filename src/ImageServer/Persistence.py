from ImageServer import Domain
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session, eagerload
from sqlalchemy.sql import select

import os


class DuplicateEntryException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, duplicateId):
        self.__duplicateId = duplicateId
        Exception.__init__(self, 'Duplicated ID: %s' % duplicateId)

    def getDuplicateId(self):
        return self.__duplicateId
    
    duplicateId = property(getDuplicateId, None, None, "DuplicateId's Docstring")


class ItemRepository():
    """ DDD repository for Original and Derived Items """
    def __init__(self, persistenceProvider):
        self.__persistenceProvider = persistenceProvider
    
    def findOriginalItemById(self, item_id):
        def callback(session):
            return session.query(Domain.OriginalItem).filter(Domain.OriginalItem.id==item_id).first() 
        return self.__persistenceProvider.do_with_session(callback)

    def findInconsistentOriginalItems(self, maxResults=100):
        def callback(session):
            # FIXME: uncomment when inheritance bug is solved
            # return session.query(Domain.OriginalItem).filter(Domain.AbstractItem.status!='STATUS_OK').limit(maxResults).all()
            return session.query(Domain.OriginalItem).filter(Domain.OriginalItem.status!='STATUS_OK').limit(maxResults).all()
            #return session.query(Domain.OriginalItem).all()
        return self.__persistenceProvider.do_with_session(callback)    
    
    def findDerivedItemByOriginalItemIdSizeAndFormat(self, item_id, size, format):
        def callback(session):
            o =  session.query(Domain.DerivedItem)\
                .filter_by(width=size[0])\
                .filter_by(height=size[1])\
                .filter_by(format=format)\
                .join('originalItem')\
                .filter_by(id=item_id)\
                .first()
                
            #o =  session.query(Domain.DerivedItem).join('originalItem').first()
            (getattr(o, 'originalItem') if hasattr(o, 'originalItem') else (lambda: None))
            return o
        return self.__persistenceProvider.do_with_session(callback)
    
    def create(self, item):
        def callback(session):
            session.save(item)
        try:
            self.__persistenceProvider.do_with_session(callback)
        except sqlalchemy.exceptions.IntegrityError, ex: 
            raise DuplicateEntryException, item.id
    
    def update(self, item):
        def callback(session):
            session.save_or_update(item)
        try:
            self.__persistenceProvider.do_with_session(callback)
        except sqlalchemy.exceptions.IntegrityError: 
            raise DuplicateEntryException, item.id
    
                           
class PersistenceProvider():
    def __init__(self, dbstring):
        self.__engine = create_engine(dbstring, encoding='utf-8', echo=False)
        self.__metadata = MetaData()
        self.__sessionmaker = sessionmaker(bind=self.__engine, autoflush=True, transactional=True)
        
        version = Table('version', self.__metadata,
            Column('name', String(255), primary_key=True),
            Column('value', Integer)
        )
        
        # FIXME: inheritance bug...
        #abstract_item = Table('abstract_item', self.__metadata,
        #    Column('id', String(255), primary_key=True),
        #    Column('status', String(255), index=True, nullable=False),
        #    Column('width', Integer, index=True, nullable=False),
        #    Column('height', Integer, index=True, nullable=False),
        #    Column('format', String(255), index=True, nullable=False),
        #    Column('type', String(255), nullable=False)
        #)
        
        original_item = Table('original_item', self.__metadata,
            Column('id', String(255), primary_key=True),
            Column('status', String(255), index=True, nullable=False),
            Column('width', Integer, index=True, nullable=False),
            Column('height', Integer, index=True, nullable=False),
            Column('format', String(255), index=True, nullable=False)  
            #Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True),
            #Column('info', String(255)),
        )
        
        derived_item = Table('derived_item', self.__metadata,
            Column('id', String(255), primary_key=True),
            Column('status', String(255), index=True, nullable=False),
            Column('width', Integer, index=True, nullable=False),
            Column('height', Integer, index=True, nullable=False),
            Column('format', String(255), index=True, nullable=False),
            #Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True),
            Column('original_item_id', String(255), ForeignKey('original_item.id', ondelete="CASCADE"))
        )

        #mapper(Domain.AbstractItem, abstract_item, polymorphic_on=abstract_item.c.type, polymorphic_identity='ABSTRACT_ITEM') 
        mapper(Domain.OriginalItem, original_item) #, inherits=Domain.AbstractItem, polymorphic_identity='ORIGINAL_ITEM'
        mapper(Domain.DerivedItem, derived_item, 
               properties={ 
                           'originalItem' : relation(Domain.OriginalItem, primaryjoin=derived_item.c.original_item_id==original_item.c.id)
                           }) #, inherits=Domain.AbstractItem , polymorphic_identity='DERIVED_ITEM' 
    
    def do_with_session(self, session_callback):
        session = self.__sessionmaker()
        o = session_callback(session)
        session.commit()
        session.close()
        return o
    
    def createOrUpgradeSchema(self):
        self.__metadata.create_all(self.__engine)
