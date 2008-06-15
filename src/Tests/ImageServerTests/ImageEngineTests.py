import unittest
from ImageServer import ImageEngine, Factory

NB_THREAD = 1


class ImageEngineTestsCase(unittest.TestCase):
    
    
    def testImageRequestProcessorMultithreadedTestCase(self):
        imageProcessor = Factory.ImageServerFactory().createImageServer('/tmp/imgserver', [(100,100), (800,800)])
        
        for i in range(NB_THREAD):
           imageProcessor.saveFileToRepository('../samples/sami.jpg', 'sami%s' %(i))
            
                              
       # request = ImageEngine.TransformationRequest('sami', (100,100), 'jpg')
        #print imageProcessor.prepareTransformation(request)

    
def suite():
    return unittest.makeSuite(ImageEngineTestsCase, 'test')
