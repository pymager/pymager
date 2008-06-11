from ImageServer import Engine, Security


def create_image_server(data_directory, allowed_sizes):
    img_processor = Engine.ImageRequestProcessor(data_directory)
    img_processor.prepare_transformation =  Security.imageTransformationSecurityDecorator(allowed_sizes)(img_processor.prepare_transformation)
    return img_processor