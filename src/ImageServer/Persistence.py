from ImageServer import Domain
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime #, UniqueConstraint
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session,backref #, eagerload
import threading
import logging
log = logging.getLogger('Persistence')

class DuplicateEntryException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, duplicateId):
        self.__duplicateId = duplicateId
        Exception.__init__(self, 'Duplicated ID: %s' % duplicateId)

    def getDuplicateId(self):
        return self.__duplicateId
    
    duplicateId = property(getDuplicateId, None, None, "The ID that lead to the DuplicateEntryException")

class NoUpgradeScriptError(Exception):
    """Thrown when no upgrade script is found for a given schema_version """
    def __init__(self, schema_version):
        self.__schema_version = schema_version
        Exception.__init__(self, 'No upgrade script is found for Schema Version: %s' % schema_version)

    def getSchemaVersion(self):
        return self.__schema_version
    
    schemaVersion = property(getSchemaVersion, None, None, "The ID that lead to the DuplicateEntryException")

class _SessionTemplate(object):
    """ Simple helper class akin to Spring-JDBC/Hibernate/ORM Template.
    It doesnt't commit nor releases resources if other do_with_session() calls are pending """
    def __init__(self, sessionmaker):
        self.__sessionmaker = sessionmaker
        self.__local = threading.local()
        
    def do_with_session(self, session_callback):        
        session = self.__sessionmaker()
        self.__local.do_with_session_count = self.__local.do_with_session_count+1 if hasattr(self.__local,'do_with_session_count') and self.__local.do_with_session_count is not None else 1   
        o = session_callback(session)
        count = self.__local.do_with_session_count
        if count == 1:
            session.commit()
            session.close()
            self.__sessionmaker.remove()
            del self.__local.do_with_session_count
        else:
            self.__local.do_with_session_count = count-1
        return o
    
class Version(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class ItemRepository(object):
    """ DDD repository for Original and Derived Items """
    def __init__(self, persistenceProvider):
        self.__persistenceProvider = persistenceProvider
        self.__template = persistenceProvider.session_template()
    
    def findOriginalItemById(self, item_id):
        """ Find an OriginalItem by its ID """
        def callback(session):
            return session.query(Domain.OriginalItem)\
                .filter(Domain.OriginalItem._id==item_id)\
                .first()
        return self.__template.do_with_session(callback)

    def findInconsistentOriginalItems(self, maxResults=100):
        """ Find Original Items that are in an inconsistent state """
        def callback(session):
            return session.query(Domain.OriginalItem)\
                .filter(Domain.AbstractItem._status!='STATUS_OK')\
                .limit(maxResults).all()
        return self.__template.do_with_session(callback)
    
    def findInconsistentDerivedItems(self, maxResults=100):
        """ Find Derived Items that are in an inconsistent state """
        def callback(session):
            return session.query(Domain.DerivedItem)\
                .filter(Domain.AbstractItem._status!='STATUS_OK')\
                .limit(maxResults).all()
        return self.__template.do_with_session(callback)
    
    def findDerivedItemByOriginalItemIdSizeAndFormat(self, item_id, size, format):
        """ Find Derived Items By :
            - the Original Item ID
            - the size of the Derived Item
            - the format of the Derived Item """
        def callback(session):
            o = session.query(Domain.DerivedItem)\
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
        """ Create a persistent instance of an item"""
        def callback(session):
            session.save(item)
        try:
            self.__template.do_with_session(callback)
        except sqlalchemy.exceptions.IntegrityError, ex: 
            raise DuplicateEntryException, item.id
    
    def update(self, item):
        """ Create a persistent instance, or update an existing item 
            @raise DuplicateEntryException: when an item with similar characteristics has already been created  
        """
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

class PersistenceProvider(object):
    """ Manages the Schema, Metadata, and stores references to the Engine and Session Maker """
    def __init__(self, dbstring):
        self.__engine = create_engine(dbstring, encoding='utf-8', echo=False, echo_pool=False, strategy='threadlocal')
        self.__metadata = MetaData()
        self.__sessionmaker = scoped_session(sessionmaker(bind=self.__engine, autoflush=True, transactional=True))
        self.__template = _SessionTemplate(self.__sessionmaker)
        
        version = Table('version', self.__metadata,
            Column('name', String(255), primary_key=True),
            Column('value', Integer)
        )
        
        abstract_item = Table('abstract_item', self.__metadata,
            Column('id', String(255), primary_key=True),
            Column('status', String(255), index=True, nullable=False),
            Column('lastStatusChangeDate', DateTime, index=True, nullable=False),
            Column('width', Integer, index=True, nullable=False),
            Column('height', Integer, index=True, nullable=False),
            Column('format', String(255), index=True, nullable=False),
            Column('type', String(255), nullable=False)
        )
        
        original_item = Table('original_item', self.__metadata,  
            Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True)
        )
        
        derived_item = Table('derived_item', self.__metadata,
            Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True),
            Column('original_item_id', String(255), ForeignKey('original_item.id', ondelete="CASCADE"))
        )

        mapper(Domain.AbstractItem, abstract_item, \
               polymorphic_on=abstract_item.c.type, \
               polymorphic_identity='ABSTRACT_ITEM', \
               column_prefix='_') 
        mapper(Domain.OriginalItem, original_item, \
               inherits=Domain.AbstractItem, \
               polymorphic_identity='ORIGINAL_ITEM', \
               column_prefix='_',
               properties={
                            'derivedItems' : relation(Domain.DerivedItem, 
                                                      primaryjoin=derived_item.c.original_item_id==original_item.c.id,
                                                      cascade='all',
                                                      backref='_originalItem' 
                                                      #backref=backref('_originalItem', 
                                                      #                cascade="refresh-expire", 
                                                      #                primaryjoin=derived_item.c.original_item_id==original_item.c.id)
                                                      ) 
                           }) 
        mapper(Domain.DerivedItem, derived_item, 
               properties={ 
                           #'_originalItem' : relation(Domain.OriginalItem, primaryjoin=derived_item.c.original_item_id==original_item.c.id, backref='derivedItems')
                           }, inherits=Domain.AbstractItem , polymorphic_identity='DERIVED_ITEM', column_prefix='_')
        mapper(Version, version)
    
    def session_template(self):
        return self.__template;
    
    def createOrUpgradeSchema(self):
        """ Create or Upgrade the database metadata
        @raise NoUpgradeScriptError: when no upgrade script is found for a given 
            database schema version
         """
        
        def get_version(session):
            schema_version = None
            try:
                schema_version = session.query(Version)\
                                    .filter(Version.name=='schema')\
                                    .first()
                schema_version = schema_version if schema_version is not None else Version('schema', 0)
            except sqlalchemy.exceptions.OperationalError:
                schema_version = Version('schema', 0) 
            return schema_version
        
        def store_latest_version(session):
            version = get_version(session)
            version.value = 1
            session.save_or_update(version)
        
        schema_version = self.__template.do_with_session(get_version)
        if schema_version.value == 0:
            log.info('Upgrading Database Schema...')
            self.__metadata.create_all(self.__engine)
            self.__template.do_with_session(store_latest_version)
        elif schema_version == 1:
            log.info('Database Schema already up to date')
            pass
        else:
            raise NoUpgradeScriptError(schema_version)
