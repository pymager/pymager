from ImageServer import Factory, Engine

def main():
    imageProcessor = Factory.ImageServerFactory().createImageServer('/tmp/imgserver', [(100,100), (800,800)])
    #img_processor.saveFileToRepository('../samples/sami.jpg', 'sami')
    request = Engine.TransformationRequest('sami', (100,100), 'jpg')
    print imageProcessor.prepareTransformation(request)
    