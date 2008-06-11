from ImageServer import Engine, Security, Persistence
import os

def create_image_server(data_directory, allowed_sizes):
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    
    persistence_provider = Persistence.SQLitePersistenceProvider(Persistence.create_connection(data_directory))
    img_processor = Engine.ImageRequestProcessor(persistence_provider, data_directory)
    img_processor.prepare_transformation =  Security.imageTransformationSecurityDecorator(allowed_sizes)(img_processor.prepare_transformation)
    return img_processor