from ImageServer import Domain
import sqlite3
import os

DB_FILENAME='db.sqlite'

def createConnection(data_directory):
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    return sqlite3.connect(os.path.join(data_directory, DB_FILENAME))

class DuplicateEntryException(Exception):
    """Thrown when errors happen while processing images """
    def __init__(self, duplicateId):
        self.__duplicateId = duplicateId
        Exception.__init__(self, 'Duplicated ID: %s' % duplicateId)

    def getDuplicateId(self):
        return self.__duplicateId
    
    duplicateId = property(getDuplicateId, None, None, "DuplicateId's Docstring")

def insertAbstractItemCallback(item):
    def insertAbstractItem(cursor):
        sql = """ INSERT INTO abstract_item (id, status, width, height, format)  VALUES (?, ?, ?, ?, ?) """
        cursor.execute(sql, (item.id, item.status, item.width, item.height, item.format))
    return insertAbstractItem

def updateAbstractItemCallback(item):
    def updateAbstractItem(cursor):
        sql = """ UPDATE abstract_item SET status=?, width=?, height=?, format=? """
        cursor.execute(sql, (item.status, item.width, item.height, item.format))
    return updateAbstractItem

class ItemRepository():
    """ DDD repository for Original and Derived Items """
    def __init__(self, persistenceProvider):
        self.__persistenceProvider = persistenceProvider
    
    def findOriginalItemById(self, item_id):
        def callback(cursor):
            # id, status, width, height, format
            sql = """ SELECT ai.id, ai.status, ai.width, ai.height, ai.format
                FROM abstract_item ai, original_item i
                WHERE ai.id = i.id 
                AND ai.id = ? """
            cursor.execute(sql, (item_id,))
            row = cursor.fetchone()
            item = None
            if row is not None:
                item_id_found, item_status, item_width, item_height, item_format = row
                item = Domain.OriginalItem(item_id_found, item_status, (item_width, item_height), item_format)
            return item
        return self.__persistenceProvider.doWithCursor(callback)

    def findDerivedItemByOriginalItemIdAndSize(self, item_id, size):
        def callback(cursor):
            # id, status, width, height, format
            sql = """ SELECT ai.id, ai.status, ai.width, ai.height, ai.format, 
                            original_abstract_item.id, original_abstract_item.status, original_abstract_item.width, original_abstract_item.height, original_abstract_item.format 
                FROM abstract_item ai, derived_item di, original_item original_item, abstract_item original_abstract_item
                WHERE ai.id = di.id 
                AND original_item.id = di.original_item_id
                AND original_item.id = ?
                AND ai.width = ?
                AND ai.height= ? """
            cursor.execute(sql, (item_id, size[0], size[1]))
            row = cursor.fetchone()
            item = None
            if row is not None:
                item_id_found, item_status, item_width, item_height, item_format, original_item_id_found, original_item_status, original_item_width, original_item_height, original_item_format = row
                original_item = Domain.OriginalItem(original_item_id_found, original_item_status, (original_item_width, original_item_height), original_item_format)
                item = Domain.DerivedItem(item_status, (item_width, item_height), item_format, original_item)
            return item
        return self.__persistenceProvider.doWithCursor(callback)
    
    
    
    def create(self, item):
        try:
            if type(item) == Domain.OriginalItem:
                self.__createOriginalItem(item)
            elif type(item) == Domain.DerivedItem:
                self.__createDerivedItem(item)
            else:
                raise ValueError("Item not recognized: %s" % type(item))
        except sqlite3.IntegrityError:
            raise DuplicateEntryException, item.id
    
    def update(self, item):
        if type(item) == Domain.OriginalItem:
            self.__updateOriginalItem(item)
        elif type(item) == Domain.DerivedItem:
            self.__updateDerivedItem(item)
        else:
            raise ValueError("Item not recognized: %s" % type(item))
    
    def __updateOriginalItem(self, item):
        self.__persistenceProvider.doWithCursor(updateAbstractItemCallback(item))
    
    def __updateDerivedItem(self, item):
        def updateDerivedItem(cursor):
            sql = """ UPDATE derived_item SET original_item_id=? """
            cursor.execute(sql, (item.originalItem.id,))
            
        self.__persistenceProvider.doWithCursor(updateAbstractItemCallback(item), updateDerivedItem)
    
    def __createOriginalItem(self, item):
        def insertOriginalItem(cursor):
            sql = """ INSERT INTO original_item (id) VALUES (?) """
            cursor.execute(sql, (item.id,))
            
        self.__persistenceProvider.doWithCursor(insertAbstractItemCallback(item), insertOriginalItem)
    
    def __createDerivedItem(self, item):
        def insertDerivedItem(cursor):
            sql = """ INSERT INTO derived_item (id, original_item_id) VALUES (?,?) """
            cursor.execute(sql, (item.id, item.originalItem.id,))
            
        self.__persistenceProvider.doWithCursor(insertAbstractItemCallback(item), insertDerivedItem)
    
                           
class SQLitePersistenceProvider():
    def __init__(self, connection):
        self.__connection = connection
    
    def createOrUpgradeSchema(self):
        c = self.__connection.cursor()
        c.execute("select count(*) from sqlite_master where type='table' and name='version'");
        val = c.fetchone()
        if val is None or val[0] == 0:
            self.__createSchema()
        
        c.close()
    
    def doWithCursor(self, *callbacks):
        c = self.__connection.cursor()
        #c.execute('BEGIN')
        for callback in callbacks:
            obj = callback(c)
        #c.execute('COMMIT')
        c.close()
        return obj
        
    def __createSchema(self):
        c = self.__connection.cursor()
        c.execute(""" CREATE TABLE version (
            name    TEXT
            value    INTEGER) """)
        
        c.execute(""" CREATE TABLE abstract_item (
            id    TEXT PRIMARY KEY,
            status TEXT,
            width    INTEGER,
            height    INTEGER,
            format    TEXT) """)
        
        c.execute(""" CREATE TABLE original_item (
            id    TEXT PRIMARY KEY,
            FOREIGN KEY(id) REFERENCES abstract_item(id)) """)
        
        c.execute(""" CREATE TABLE derived_item (
            id    TEXT PRIMARY KEY,
            original_item_id  TEXT,
            FOREIGN KEY(id) REFERENCES abstract_item(id),
            FOREIGN KEY(original_item_id) REFERENCES original_item(id)) """)
        c.close()
        