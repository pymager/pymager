
class DeleteImagesCommand(object):
    """ Coordinates the deletion of an image metadata and files """
    
    def __init__(self, item_repository, session_template, fetch_items_callback, delete_file_callback):
        """ Initializes a Delete Images Command with the following parameters
            @param item_repository: the repository for image metadata
            @param session_template: the db session template
            @param fetch_items_callback: some function that will return a list of image metadata
            @param delete_file_callback: some function that will delete the file associated to a given metadata
        """
        self.__item_repository = item_repository
        self.__session_template = session_template
        self.__fetch_items_callback = fetch_items_callback
        self.__delete_file_callback = delete_file_callback
        
    def __cleanup_in_session(self, fetch_items, delete_file):
        items = fetch_items()
        for i in items:
            delete_file(i)
            self.__item_repository.delete(i)
        
    def execute(self):
        def execute_in_session(session):
            self.__cleanup_in_session(self.__fetch_items_callback, self.__delete_file_callback)
        self.__session_template.do_with_session(execute_in_session)
    