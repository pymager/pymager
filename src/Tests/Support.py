import unittest
from ImageServer import Factory, ImageEngine
import os, shutil
 
class AbstractIntegrationTestCase(unittest.TestCase):
        
    DATA_DIRECTORY='/tmp/imgserver-test'
    
    def __cleanup__(self):
        if os.path.exists(AbstractIntegrationTestCase.DATA_DIRECTORY):
            shutil.rmtree(AbstractIntegrationTestCase.DATA_DIRECTORY)
            
                
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.__cleanup__()
        
        self.imageServerFactory = Factory.ImageServerFactory()
        self.imgProcessor = self.imageServerFactory.createImageServer(AbstractIntegrationTestCase.DATA_DIRECTORY, [(100,100), (800,800)])
    
        (getattr(self, 'onSetUp') if hasattr(self, 'onSetUp') else (lambda: None))()  
        
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        (getattr(self, 'onTearDown') if hasattr(self, 'onTearDown') else (lambda: None))()
        self.__cleanup__()
        
        #self.imageServerFactory.getConnection().close()
    
    