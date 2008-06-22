import unittest, os, time, random
from Tests import Support
from ImageServer import ImageEngine, Domain
from threading import Thread


NB_THREADS = 15

JPG_SAMPLE_IMAGE_FILENAME = os.path.join('..', '..', '..','samples', 'sami.jpg')
JPG_SAMPLE_IMAGE_SIZE = (3264, 2448)
BROKEN_IMAGE_FILENAME = os.path.join('..', '..', '..','samples', 'brokenImage.jpg')

class ImageEngineTestsCase(Support.AbstractIntegrationTestCase):
    
    def testImageIdShouldOnlyContainAlphanumericCharacters(self):
        try:
            self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId-')
        except ImageEngine.IDNotAuthorized, ex:
            assert ex.imageId == 'sampleId-'
    
    def testSaveBrokenImageShouldThrowException(self):
        try:
            self._imgProcessor.saveFileToRepository(BROKEN_IMAGE_FILENAME, 'sampleId')
        except ImageEngine.ImageFileNotRecognized, ex:
            pass
    
    def testSaveImageWithExistingIDShouldThrowException(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        try:
            self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')    
        except ImageEngine.ImageIDAlreadyExistingException, ex:
            assert ex.imageId == 'sampleId'
    
    def testSaveImageShouldUpdateFileSystemAndDatabase(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        assert os.path.exists(os.path.join(Support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')) == True
        
        item = self._itemRepository.findOriginalItemById('sampleId')
        assert item is not None
        assert item.id == 'sampleId'
        assert item.format == Domain.IMAGE_FORMAT_JPEG
        assert item.size == JPG_SAMPLE_IMAGE_SIZE
        assert item.status == Domain.STATUS_OK
        
    def testPrepareTransformationWithNonExistingOriginalIdShouldThrowException(self):
        try:
            request = ImageEngine.TransformationRequest('nonexisting', (100,100), Domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
    
    def testPrepareRequestShouldUpdateFileSystemAndDatabase(self):
        self._imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        request = ImageEngine.TransformationRequest('sampleId', (100,100), Domain.IMAGE_FORMAT_JPEG)
        result = self._imgProcessor.prepareTransformation(request)
        assert os.path.exists(os.path.join(Support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'sampleId-100x100.jpg')) == True
        
        item = self._itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('sampleId', (100,100), Domain.IMAGE_FORMAT_JPEG)
        assert item is not None
        assert item.id == 'sampleId-100x100-JPEG'
        assert item.format == Domain.IMAGE_FORMAT_JPEG
        assert item.size == (100,100)
        assert item.status == Domain.STATUS_OK
        assert item.originalItem.id == 'sampleId'
        
        # result should be consistent across calls (caching..)
        result2 = self._imgProcessor.prepareTransformation(request)
        assert result == os.path.join('cache', 'sampleId-100x100.jpg')
        assert result2 == os.path.join('cache', 'sampleId-100x100.jpg')
    
    def koImageRequestProcessorMultithreadedTestCase(self):
        
        children = []
        for i in range(NB_THREADS):
            currentThread = SaveImageToRepositoryThread(self._imgProcessor, "sami%s" %(i))
            currentThread.start()
            children.append(currentThread)
        
        #Randomize sleeping float , 0.0 <= x < 1.0
        #time.sleep(random.random())
        #time.sleep(2)
        
        k = 0
        for thread in children:
            thread.join()
            assert os.path.exists(os.path.join(Support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sami%s.jpg' %(k))) == True
            k=k+1
    
    

class SaveImageToRepositoryThread(Thread):
    def __init__ (self, imgProcessor, itemid):
        Thread.__init__(self)
        self.__imgProcessor = imgProcessor
        self.__itemid = itemid


    def run(self):
            self.__imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, self.__itemid)

        
    
def suite():
    return unittest.makeSuite(ImageEngineTestsCase, 'test')
