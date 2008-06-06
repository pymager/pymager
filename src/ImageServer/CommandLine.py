from ImageServer import Core

def main():
    request = Core.ImageRequest('sami', (800,800), 'jpg')
    img_processor = Core.ImageRequestProcessor('/tmp')
    
    img_processor.prepare_request(request);