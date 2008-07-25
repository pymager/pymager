import unittest
from imgserver import factory
from imgserver.factory import ServiceConfiguration
import sqlalchemy 
import os, shutil
 
class AbstractIntegrationTestCase(unittest.TestCase):
        
    DATA_DIRECTORY='/tmp/imgserver-test'
    SAURI = 'sqlite:///:memory:'
    #SAURI = 'postgres://imgserver:funala@localhost/imgserver'
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        sqlalchemy.orm.clear_mappers()
        
        config = ServiceConfiguration(
            data_directory=AbstractIntegrationTestCase.DATA_DIRECTORY, 
            dburi=AbstractIntegrationTestCase.SAURI, 
            allowed_sizes=[(100*i,100*i) for i in range(1,9)],
            dev_mode= True)
        
        self._imageServerFactory = factory.ImageServerFactory(config)
        self._imgProcessor = self._imageServerFactory.createImageServer()
        self._itemRepository = self._imageServerFactory.getItemRepository()        
    
        (getattr(self, 'onSetUp') if hasattr(self, 'onSetUp') else (lambda: None))()  
        
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        (getattr(self, 'onTearDown') if hasattr(self, 'onTearDown') else (lambda: None))()
        self._imageServerFactory = None
        self._imgProcessor = None
        self._itemRepository = None
        self._persistenceProvider = None
        
        #self.imageServerFactory.getConnection().close()
    