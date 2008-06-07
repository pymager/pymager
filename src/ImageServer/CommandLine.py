from ImageServer import Core

def main():
    img_processor = Core.ImageRequestProcessor('/tmp/imgserver')
    img_processor.save_file_to_repository('../samples/sami.jpg', 'sami')
    request = Core.TransformationRequest('sami', (100,100), 'jpg')
    #request = Core.TransformationRequest('sami', (3264,2448), 'JPEG')
    print img_processor.prepare_transformation(request);