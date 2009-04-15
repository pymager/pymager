import os

class DeleteImagesCommand(object):
    """ Coordinates the deletion of an image metadata and files """
    
    def __init__(self, item_repository, session_template, path_generator, fetch_items_callback):
        """ Initializes a Delete Images Command with the following parameters
            @param item_repository: the repository for image metadata
            @param session_template: the db session template
            @param path_generator: a PathGenerator instance
            @param fetch_items_callback: some function that will return a list of image metadata
            
        """
        self.__item_repository = item_repository
        self.__path_generator = path_generator
        self.__session_template = session_template
        self.__fetch_items_callback = fetch_items_callback
        
    def __cleanup_in_session(self, fetch_items):
        items = fetch_items()
        for i in items:
            os.remove(i.associated_image_path(self.__path_generator).absolute())
            self.__item_repository.delete(i)
        
    def execute(self):
        def execute_in_session(session):
            self.__cleanup_in_session(self.__fetch_items_callback)
        self.__session_template.do_with_session(execute_in_session)
    