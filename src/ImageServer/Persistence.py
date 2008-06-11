import sqlite3
import os

DB_FILENAME='db.sqlite'

def create_connection(data_directory):
    return sqlite3.connect(os.path.join(data_directory, DB_FILENAME))
                           
class SQLitePersistenceProvider():
    def __init__(self, connection):
        self.__connection = connection
    
    def create_or_upgrade_schema(self):
        pass
    


