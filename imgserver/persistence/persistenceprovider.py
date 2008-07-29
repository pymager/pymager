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

log = logging.getLogger('persistence.persistenceprovider')

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
    It doesnt't commit nor releases resources if other do_with_session() calls are pending
    
    See http://www.sqlalchemy.org/trac/ticket/1084#comment:3 for suggestions on how to improve this
    without using a custom threadlocal variable
     """
    def __init__(self, sessionmaker):
        self.__sessionmaker = sessionmaker
        self.__local = threading.local()
        
    def do_with_session(self, session_callback):        
        session = self.__sessionmaker()
        self.__local.do_with_session_count = self.__local.do_with_session_count+1 if hasattr(self.__local,'do_with_session_count') and self.__local.do_with_session_count is not None else 1
        
        def cleanup_on_exception(f):
            try:
                return f()
            except Exception, ex:
                del self.__local.do_with_session_count
                try:
                    conn = session.connection().invalidate()
                except sqlalchemy.exceptions.InvalidRequestError:
                    # ignore the following exception that happens on windows... 
                    # InvalidRequestError("The transaction is inactive 
                    # due to a rollback in a subtransaction and should be closed")
                    #
                    pass
                except Exception:
                    pass
                #conn.close()
                session.rollback()
                session.close()
                self.__sessionmaker.remove()
                raise ex
        
        def do():
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
        
        return cleanup_on_exception(do)
    
    
class Version(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class IPersistenceProvider(Interface):
    """ Manages the Schema, Metadata, and stores references to the Engine and Session Maker """
    
    def createOrUpgradeSchema(self):
        """ Create or Upgrade the database metadata
        @raise NoUpgradeScriptError: when no upgrade script is found for a given 
            database schema version """
            
    def drop_all_tables(self):
        """ Drop all tables """
        
    def session_template(self):
        """ Creates a Spring JDBC-like template """
         
class PersistenceProvider(object):
    implements(IPersistenceProvider)
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

        mapper(AbstractItem, abstract_item, \
               polymorphic_on=abstract_item.c.type, \
               polymorphic_identity='ABSTRACT_ITEM', \
               column_prefix='_') 
        mapper(OriginalItem, original_item, \
               inherits=AbstractItem, \
               polymorphic_identity='ORIGINAL_ITEM', \
               column_prefix='_',
               properties={
                            'derivedItems' : relation(DerivedItem, 
                                                      primaryjoin=derived_item.c.original_item_id==original_item.c.id,
                                                      cascade='all',
                                                      backref='_originalItem' 
                                                      #backref=backref('_originalItem', 
                                                      #                cascade="refresh-expire", 
                                                      #                primaryjoin=derived_item.c.original_item_id==original_item.c.id)
                                                      ) 
                           }) 
        mapper(DerivedItem, derived_item, 
               properties={ 
                           #'_originalItem' : relation(OriginalItem, primaryjoin=derived_item.c.original_item_id==original_item.c.id, backref='derivedItems')
                           }, inherits=AbstractItem , polymorphic_identity='DERIVED_ITEM', column_prefix='_')
        mapper(Version, version)
    
    def session_template(self):
        return self.__template;
    
    def drop_all_tables(self):
        self.__metadata.drop_all(self.__engine)
    
    def createOrUpgradeSchema(self):
        def get_version(session):
            schema_version = None
            try:
                schema_version = session.query(Version)\
                                    .filter(Version.name=='schema')\
                                    .first()
                schema_version = schema_version if schema_version is not None else Version('schema', 0)
            except sqlalchemy.exceptions.OperationalError:
                schema_version = Version('schema', 0)
            except sqlalchemy.exceptions.ProgrammingError:
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
        elif schema_version.value == 1:
            log.info('Database Schema already up to date')
        else:
            raise NoUpgradeScriptError(schema_version)
