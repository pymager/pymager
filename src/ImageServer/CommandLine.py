from ImageServer import Factory, Engine

def main():
    img_processor = Factory.create_image_server('/tmp/imgserver', [(100,100), (800,800)])
    # uncomment if not already done once
    #img_processor.save_file_to_repository('../samples/sami.jpg', 'sami')
    request = Engine.TransformationRequest('sami', (100,100), 'jpg')
    print img_processor.prepare_transformation(request);
    