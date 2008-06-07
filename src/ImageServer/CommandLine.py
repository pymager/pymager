from ImageServer import Core

def main():
    img_processor = Core.ImageRequestProcessor('/tmp')
    img_processor.save_file_to_repository('../samples/sami.jpg', 'sami')
    request = Core.TransformationRequest('sami', (100,100), 'jpg')
    img_processor.prepare_transformation(request);