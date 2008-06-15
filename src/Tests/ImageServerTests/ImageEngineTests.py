import unittest
from Tests import Support

NB_THREAD = 1


class ImageEngineTestsCase(Support.AbstractIntegrationTestCase):
    
    
    def testImageRequestProcessorMultithreadedTestCase(self):
        #imageProcessor = Factory.ImageServerFactory().createImageServer('/tmp/imgserver', [(100,100), (800,800)])

        for i in range(NB_THREAD):
            self.imgProcessor.saveFileToRepository('../../../samples/sami.jpg', 'sami%s' %(i))

            
                              
       # request = ImageEngine.TransformationRequest('sami', (100,100), 'jpg')
        #print imageProcessor.prepareTransformation(request)

    
def suite():
    return unittest.makeSuite(ImageEngineTestsCase, 'test')
