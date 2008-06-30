import shutil
from imgserver import factory, domain
from imgserver.imgengine.transformationrequest import TransformationRequest

DB_FILENAME='db.sqlite'

def main():
    shutil.rmtree('/tmp/imgserver',True)
    f = factory.ImageServerFactory()
    imageProcessor = f.createImageServer('/tmp/imgserver', 'sqlite:////tmp/imgserver/%s' % DB_FILENAME, [(100,100), (800,800)])
    imageProcessor.saveFileToRepository('samples/sami.jpg', 'sami')
    request = TransformationRequest('sami', (100,100), domain.IMAGE_FORMAT_JPEG)
    print imageProcessor.prepareTransformation(request)