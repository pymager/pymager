import unittest
from ImageServer import Factory, Engine
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
        self.img_processor = self.imageServerFactory.createImageServer('/tmp/imgserver', [(100,100), (800,800)])
    
        (getattr(self, 'onSetUp') if hasattr(self, 'onSetUp') else (lambda: None))()  
        
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        (getattr(self, 'onTearDown') if hasattr(self, 'onTearDown') else (lambda: None))()
        
        self.imageServerFactory.getConnection().close()  
    
    