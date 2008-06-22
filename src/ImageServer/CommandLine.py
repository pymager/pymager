from ImageServer import Factory, ImageEngine

DB_FILENAME='db.sqlite'

def main():
    factory = Factory.ImageServerFactory()
    imageProcessor = factory.createImageServer('/tmp/imgserver', 'sqlite:///:memory:', [(100,100), (800,800)])
    #imageProcessor.saveFileToRepository('../samples/sami.jpg', 'sami')
    #request = ImageEngine.TransformationRequest('sami', (100,100), 'JPEG')
    #print imageProcessor.prepareTransformation(request)