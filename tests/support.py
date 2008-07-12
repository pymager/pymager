import unittest
from imgserver import factory, imgengine
import sqlalchemy 
import os, shutil
 
class AbstractIntegrationTestCase(unittest.TestCase):
        
    DATA_DIRECTORY='/tmp/imgserver-test'
    SAURI = 'sqlite:///:memory:'
    #SAURI = 'postgres://imgserver:funala@localhost/imgserver'
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        sqlalchemy.orm.clear_mappers()
        
        self._imageServerFactory = factory.ImageServerFactory()
        self._imgProcessor = self._imageServerFactory.createImageServer(AbstractIntegrationTestCase.DATA_DIRECTORY, AbstractIntegrationTestCase.SAURI, [(100*i,100*i) for i in range(1,9)], True)
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
    