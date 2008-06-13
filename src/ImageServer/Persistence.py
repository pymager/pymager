import sqlite3
import os

DB_FILENAME='db.sqlite'

def create_connection(data_directory):
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    return sqlite3.connect(os.path.join(data_directory, DB_FILENAME))
                           
class SQLitePersistenceProvider():
    def __init__(self, connection):
        self.__connection = connection
    
    def create_or_upgrade_schema(self):
        c = self.__connection.cursor()
        
        c.execute("select count(*) from sqlite_master where type='table' and name='version'");
        val = c.fetchone()
        if val is None or val[0] == 0:
            self.create_schema()
        
    def create_schema(self):
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
        
    


