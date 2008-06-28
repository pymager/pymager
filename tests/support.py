import unittest
from imgserver import factory, imgengine
import sqlalchemy 
import os, shutil
 
class AbstractIntegrationTestCase(unittest.TestCase):
        
    DATA_DIRECTORY='/tmp/imgserver-test'
    
    def __cleanup__(self):
        if os.path.exists(AbstractIntegrationTestCase.DATA_DIRECTORY):
            shutil.rmtree(AbstractIntegrationTestCase.DATA_DIRECTORY)
            
                
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.__cleanup__()
        sqlalchemy.orm.clear_mappers()
        
        self._imageServerFactory = factory.ImageServerFactory()
        self._imgProcessor = self._imageServerFactory.createImageServer(AbstractIntegrationTestCase.DATA_DIRECTORY, 'sqlite:///:memory:', [(100*i,100*i) for i in range(1,9)])
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
    
    