from ImageServer import Factory, ImageEngine

def main():
    factory = Factory.ImageServerFactory()
    imageProcessor = factory.createImageServer('/tmp/imgserver', [(100,100), (800,800)])
    #imageProcessor.saveFileToRepository('../samples/sami.jpg', 'sami')
    request = ImageEngine.TransformationRequest('sami', (100,100), 'jpg')
    print imageProcessor.prepareTransformation(request)