from ImageServer import Core, Security


def create_image_server(data_directory, allowed_sizes):
    img_processor = Core.ImageRequestProcessor(data_directory)
    
    # add interceptors
    img_processor.prepare_transformation =  Security.imageTransformationSecurityDecorator(allowed_sizes)(img_processor.prepare_transformation)
    
    return img_processor